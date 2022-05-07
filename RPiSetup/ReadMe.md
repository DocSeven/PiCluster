# Basic Set-Up of Raspberry Pi Devices

This section describes how to get a Raspberry Pi up and running, so we can
install the cluster software later on. The assumption is that we start with a
new RPi from scratch. If you have already installed the operating system and
updated it, you can skip the first couple of steps. All you need to to do is
change the hostname and configure a static IP-address (last part of the
section "Preparing the First Boot").


We use four RPis (RPi 4, Model B with 8 GB RAM), four SD-cards each with at
least 32 GB capacity, and a switch with at least five connections for
connecting the RPis with your machine and each other. When this project started, the 64-bit version of Raspbian
was not available yet, so we used the 32-bit version. Now that the 64-bit
version is stable and has been released, this should also work (we have not
tested it, though). 


## Flashing the Operating System

First of all you need to prepare the SD-cards. Head to the [Raspberry web
page](https://www.raspberrypi.com/software/operating-systems/)
to download an image for flashing the operating system to an SD-card.
Be sure to download the full version including recommended software (the
largest file at around 2.2 GB). For our own cluster, we are currently using
[Buster](https://downloads.raspberrypi.org/raspios_full_armhf/images/raspios_full_armhf-2021-05-28/).
However, the current version available on the front page should also work, we
just have not tried it out.
Once you have downloaded the image, you can flash it to an SD-card. We assume
that an SD-card reader/writer is available. We used
[Etcher](https://www.balena.io/etcher/) for flashing the image. 


You can also watch the instructional video below. While this describes the
general steps, some of the parameters used in the video, e.g. the IP-addresses
and hostnames, are different from the setup described in the text below. So,
please read the text before starting with the configuration. The second half
of the video shows how to prepare the RPis for the cluster software using
ansible. A detailed description of this process can be found in the ReadMe
file in the Ansible directory.

<div align="center">
  <a href="https://www.youtube.com/watch?v=-xZRUxrKbsY">
    <img src="images/setup.png" alt="PiCluster Setup" style="width:30%;">
  </a>
</div>



## Preparing the First Boot

As we are installing a headless system, i.e., we do not connect the RPis to a
monitor, we also need to make sure that we can log onto an RPi using
ssh. Additionally, we configure a static IP-address. Mount the two partitions
"boot" and "rootfs" of the SD-card on the machine you used for flashing the
image and go to the "boot" partition. Create an empty file "ssh", this will
allow you to access the RPi via ssh. For instance, in Linux you would use the
command

```bash
touch ssh
```

Then switch to the "rootfs" partition and go to the directory "etc". Open the
file "dhcpcd.conf" and scroll down to the section showing an example for
configuring a static IP-address. Replace whatever is there with

```bash
interface eth0
static ip_address=10.42.0.xxx/24
static routers=10.42.0.1
static domain_name_servers=10.42.0.1 8.8.8.8
```

The "xxx" stands for 250, 251, 252, or 253. We will use the four static
IP-addresses 10.42.0.250, 10.42.0.251, 10.42.0.252, and 10.42.0.253 for our
cluster, so you assign each of these IP-addresses to one of the RPis.
This assumes that you configured a wired (ethernet) connection on
your machine that shares the wifi connection and that this ethernet connection
uses the address space 10.42.0.0/24. For more detailed instructions on how to
do this, see e.g. https://www.tecmint.com/share-internet-in-linux/


When you plug the SD-cards into the RPis, it is a good idea to remember which
SD-card was configured with which IP-address. You can mark the RPis or the
SD-cards with a permanent marker.


## Booting

Connect your machine and the RPis to the switch, power everything up, and activate the shared network
(10.42.0.0/24) on your machine. The RPis should now boot and after a while be
accessible via ssh. Connect to each of the RPis in turn via ssh to do some
basic configurations (the password is "raspberry"):

```bash
ssh pi@10.42.0.xxx
```

Once you are logged in, enable ssh permanently and call raspi-config for some
basic configurations:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo raspi-config
```

Under system options, set the name of the RPi according to the table
below. Also expand the rootfs (can be found under advanced options). When
leaving raspi-config, it will ask you whether you want to reboot. Confirm
this.

| Hostname   | IP Address  |
| ---------- | ----------- |
| rpi0       | 10.42.0.250 |
| rpi1       | 10.42.0.251 |
| rpi2       | 10.42.0.252 |
| rpi3       | 10.42.0.253 |


## Updating the Operating System

After rebooting the RPis, connect to each of them via ssh again and update the
operating system:

```bash
sudo apt update
sudo apt full-upgrade
```

Some issue we ran into when updating the RPis were the following:

* The RPis could not connect to a nameserver, even though the "dhcpcd.conf"
  file was correctly configured. This may be a problem with the firewall, as a
  workaround on our machine, we switched off the firewall and restarted the
  ethernet connection sharing the wifi.

* The update process terminates with an error. Try restarting the full-upgrade
  with the parameter --fix-missing:
  ```bash
  sudo apt full-upgrade --fixmissing
  ```
  If this does not work, restart the whole update process (again using
  --fix-missing if you run into errors):
  ```bash
  sudo apt clean
  sudo apt update
  sudo apt full-upgrade 
  ```
  


