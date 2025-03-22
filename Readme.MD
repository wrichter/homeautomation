# Home Automation using Microshift on Fedora IOT / RasPi 4

Based on Fedora IoT / Fedora 36 and containerized MicroShift based on OpenShift 4.8. 
Given that MicroShift is undergoing rapid development, the notes are already outdated at the time of publishing.


<!--
```plantuml
@startuml componentmodel.svg

node rpi as "Raspberry Pi4 8GB" {

    interface Router as "HTTP"
    package microshift {

        package mqtt {
            interface MQTT
            component mosquitto
            MQTT - mosquitto
        }

        package zigbee2mqtt {
            interface HTTP_Zigbee2MQTT as "HTTP"
            component zigbee2mqtt_comp as "Zigbee2MQTT" 
            HTTP_Zigbee2MQTT - zigbee2mqtt_comp
            database Zigbee2MQTT_PVC as "Zigbee2MQTT" <<PVC>> 
            zigbee2mqtt_comp -- Zigbee2MQTT_PVC
        }
        zigbee2mqtt_comp -down-> MQTT

        /'package ns_homebridge as "homebridge" {
            interface HTTP_homebridge as "HTTP"
            component homebridge_comp as "Homebridge" 
            HTTP_homebridge - homebridge_comp
            database Homebridge_PVC as "Homebridge" <<PVC>> 
            homebridge_comp -- Homebridge_PVC
        }
        homebridge_comp -down-> MQTT'/


        package ns_homeassistant as "homeassistant" {
            interface HTTP_Homeassistant as "HTTP"
            component homeassistant_comp as "Home Assistant"
            HTTP_Homeassistant - homeassistant_comp
            database Homeassistant_PVC as "Homeassistant" <<PVC>>
            homeassistant_comp -- Homeassistant_PVC
        }
        homeassistant_comp -down-> MQTT

        package ns_volkszaehler as "volkszaehler" {
            'component weather_comp as "Weather" <<custom code>>

            component vzlogger_comp as "VZLogger"
            interface HTTP_VZLogger as "HTTP"
            HTTP_VZLogger - vzlogger_comp

            interface HTTP_Volkszaehler as "HTTP"
            component Volkszaehler_comp as "Volkszaehler" <<Middleware & UI>>
            HTTP_Volkszaehler - Volkszaehler_comp

            interface HTTP_Pushserver as "HTTP"
            component Pushserver_comp as "Push Server"
            HTTP_Pushserver - Pushserver_comp

            interface SQL as "SQL"
            component Volkszaehler_db as "Volkszaehler DB" <<MySQL>>
            SQL - Volkszaehler_db
            database Database_PVC as "Database" <<PVC>> 
            Volkszaehler_db -- Database_PVC

            'weather_comp -down-> HTTP_Volkszaehler
            vzlogger_comp -down-> HTTP_Volkszaehler 
            vzlogger_comp -down-> HTTP_Pushserver 
            Volkszaehler_comp -down-> SQL

        }
        vzlogger_comp -down-> MQTT 

        package ns_nodered as "node-red" {
            interface HTTP_nodered as "HTTP"
            component nodered_comp as "Node Red"
            HTTP_nodered - nodered_comp
            database nodered_PVC as "node-red" <<PVC>>
            nodered_comp -- nodered_PVC
        }
        MQTT <-down- nodered_comp
        HTTP_Homeassistant <-down- nodered_comp
        HTTP_Pushserver <-down- nodered_comp
        HTTP_Volkszaehler <-down- nodered_comp
    }
    Router - microshift 
    Router ..> HTTP_Volkszaehler : http://volkszaehler.local
    Router ..> HTTP_Pushserver : http://volkszaehler.local/ws
    Router ..> HTTP_Homeassistant : http://homeassistant.local
    'Router ..> HTTP_homebridge : http://homebridge.local
    Router ..> HTTP_Zigbee2MQTT : http://zigbee2mqtt.local
    Router ..> HTTP_VZLogger : http://vzlogger.local
    Router ..> HTTP_nodered : http://node-red.local


    component meterserialinterface_comp as "USB IR RW-Head" <<USB Device>>
    meterserialinterface_comp -- vzlogger_comp  

    component onewiresensors_comp as "One Wire Subsystem" <<GPIO Device>>
    onewiresensors_comp -- vzlogger_comp 

    component impulsecounter_comp as "GPIO Pin" <<GPIO Device>>
    impulsecounter_comp -- vzlogger_comp  

    component zigbee_dongle as "Zigbee Dongle" <<USB Device>>
    zigbee_dongle -- zigbee2mqtt_comp
    


    rectangle ha_integration_description [
        //integration of many//
        //smart home devices and services//
        //with Apple HomeKit//
    ]
    ha_integration_description -- homeassistant_comp
    'ha_integration_description -- homebridge_comp
}

cloud home_network as "Home LAN"
home_network -- Router

cloud zigbee_network as "Zigbee"
zigbee_network -- zigbee_dongle

collections smart_meters as "Smart Electricity Meters"
smart_meters -- meterserialinterface_comp 

agent weather_api as "Weather API"
'weather_api -- weather_comp 
weather_api -- ha_integration_description

collections onewire_sensors as "One Wire Temperature Sensors"
onewire_sensors -- onewiresensors_comp

agent gas_meter as "Gas Meter Impulse Counter"
gas_meter -- impulsecounter_comp 

agent apple_homekit as "Apple HomeKit"
apple_homekit -- ha_integration_description

collections ha_integrations as "Smart Home Integrations"
ha_integrations -- ha_integration_description

'agent zigbee_bridge as "Zigbee Bridge"
'zigbee_bridge -- ha_integration_description

@enduml
```
-->

![Component Model](componentmodel.png?raw=true "Component Model")





### Resize Partition

Fedora 38: If the `resize2fs` command fails, check if the device is mounted as read-only `/sysroot` and if so, remount rw before attempting resize: `mount -o remount,rw /sysroot`. Reboot after resizing: `systemctl reboot`.


```bash
[root@p200300cfaf07d500c73722aece5bd6e0 ~]# parted
GNU Parted 3.4
Using /dev/mmcblk0
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) p
Model: SD SN64G (sd/mmc)
Disk /dev/mmcblk0: 63.9GB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:
 
Number  Start   End     Size    Type     File system  Flags
 1      1049kB  526MB   525MB   primary  fat16        boot
 2      526MB   1600MB  1074MB  primary  ext4
 3      1600MB  4294MB  2694MB  primary  ext4
 
(parted) resizepart 3
Warning: Partition /dev/mmcblk0p3 is being used. Are you sure you want to continue?
Yes/No? Yes
End?  [4294MB]? 63.9GB
(parted) p
Model: SD SN64G (sd/mmc)
Disk /dev/mmcblk0: 63.9GB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:
 
Number  Start   End     Size    Type     File system  Flags
 1      1049kB  526MB   525MB   primary  fat16        boot
 2      526MB   1600MB  1074MB  primary  ext4
 3      1600MB  63.9GB  62.3GB  primary  ext4
 
(parted) quit

[root@p200300cfaf07d500c73722aece5bd6e0 ~]# resize2fs /dev/mmcblk0p3
resize2fs 1.46.3 (27-Jul-2021)
Filesystem at /dev/mmcblk0p3 is mounted on /sysroot; on-line resizing required
old_desc_blocks = 1, new_desc_blocks = 8
The filesystem on /dev/mmcblk0p3 is now 15201280 (4k) blocks long.
```



### Configure System (hostname, time zone)

```bash
timedatectl set-timezone Europe/Berlin
#microshift.local required for mDNS
hostnamectl set-hostname microshift.local
echo "127.0.0.1 microshift microshift.local" >> /etc/hosts
```

### Disable systemd-resolved stub 
So that containers get the upstream DNS configured, flannel conflicts with systemd-resolved 

```bash
sed -i 's/^.\?DNSStubListener=.*$/DNSStubListener=no/' /etc/systemd/resolved.conf
```

### Install CRIO + GIT + AVAHI/mDNS

Fedora 36:
```bash
curl -L -o /etc/yum.repos.d/fedora-modular.repo https://src.fedoraproject.org/rpms/fedora-repos/raw/rawhide/f/fedora-modular.repo 
curl -L -o /etc/yum.repos.d/fedora-updates-modular.repo https://src.fedoraproject.org/rpms/fedora-repos/raw/rawhide/f/fedora-updates-modular.repo 
```

Fedora 38
```bash
rpm-ostree install fedora-repos-modular
systemctl reboot
```


```bash
curl -L -o /etc/yum.repos.d/group_redhat-et-microshift-fedora-36.repo https://copr.fedorainfracloud.org/coprs/g/redhat-et/microshift/repo/fedora-36/group_redhat-et-microshift-fedora-36.repo

rpm-ostree update
rpm-ostree ex module enable cri-o:1.21
rpm-ostree install cri-o cri-tools git nss-mdns avahi
systemctl reboot

systemctl enable --now avahi-daemon.service

```

### Configure Microshift (disabled since the defaults work well & .local as domain can be used for mDNS)

```bash
mkdir /etc/microshift/
cat - > /etc/microshift/config.yaml <<EOF
cluster:
  domain: microshift.fritz.box
EOF
mv /etc/microshift/config.yaml /etc/microshift/config-disabled.yaml
``` 

### Open Firewall Ports
see also https://microshift.io/docs/user-documentation/networking/firewall/
```bash
firewall-cmd --zone=trusted --add-source=10.42.0.0/16 --permanent
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent
firewall-cmd --zone=public --add-port=5353/udp --permanent
firewall-cmd --zone=public --add-port=6443/tcp --permanent
firewall-cmd --reload
```


### Enable MicroShift via Podman

#### Enable Podman Service
```bash
curl -o /etc/systemd/system/microshift.service \
     https://raw.githubusercontent.com/redhat-et/microshift/main/packaging/systemd/microshift-containerized.service
systemctl enable microshift --now
```

#### Copy credentials
```bash
mkdir ~/.kube
sudo podman cp microshift:/var/lib/microshift/resources/kubeadmin/kubeconfig ~/.kube/config
sudo chown `whoami`: ~/.kube/config
```

### OR: Enable MicroShift via RPM
#### Enable Podman Service
```bash
rpm-ostree install microshift
systemctl reboot
[...]
systemctl enable microshift --now
```

#### Copy Credentials
```bash
mkdir ~/.kube
sudo cat /var/lib/microshift/resources/kubeadmin/kubeconfig > ~/.kube/config
```


### Install OpenShift Client

```bash
curl -# -L -o /tmp/openshift-client-linux.tar.gz https://mirror.openshift.com/pub/openshift-v4/aarch64/clients/ocp/stable-4.10/openshift-client-linux.tar.gz \
 && tar xzvf /tmp/openshift-client-linux.tar.gz -C /usr/local/bin/ oc kubectl \
 && chmod +x /usr/local/bin/oc /usr/local/bin/kubectl \
 && rm /tmp/openshift-client-linux.tar.gz
 ```



 ## Workload Config

 ### Enable 1-wire interface on gpio4
 ```bash
echo -n "dtoverlay=w1-gpio,gpiopin=4" >>/boot/efi/config.txt
rpm-ostree install kernel-modules-extra #give access to w1_therm
systemctl reboot
 ```

 ### Enable access to gpiochip0 to normal users
 ```bash
chmod a+rw /dev/gpiochip0
 ```


 ### Allow Network Ports for Homebridge

Enable Ingress Traffic on Node Ports 30010-30030. This range has been chosen since it is also in the NodePort range:

 ```bash
firewall-cmd --zone=public --add-port=30010-30030/tcp --permanent
firewall-cmd --reload
 ```

Homebridge runs on the host network. You need to configure homebridge to use the 
ports which have been exposed.
 ```json
 {
    "bridge": {
        "name": "Homebridge",
        "username": "59:73:93:78:B4:DA",
        "port": 30010,
        "pin": "998-42-561",
        "advertiser": "avahi"
    },
    "ports": {
        "start": 30012,
        "end": 30019
    },
    "description": "Home Smart Home",
    "platforms": [
        {
            "platform": "config",
            "name": "Config",
            "port": 8581,
            "auth": "form",
            "theme": "red"
        },
        {
            "name": "Sonos",
            "brightness": true,
            "excludeAirPlay": false,
            "nameScheme": "% Lärm",
            "address": "192.168.10.54",
            "port": 30011,
            "service": "switch",
            "speakers": true,
            "tv": true,
            "platform": "ZP"
        },
 ```


## HomeAssistant

## for sonos
```
# firewall-cmd --add-port=1400/tcp --permanent
# firewall-cmd --reload
```

## for homekit

```
# firewall-cmd --add-port=21064-21080/tcp --permanent
# firewall-cmd --reload
```