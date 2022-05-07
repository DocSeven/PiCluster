# Ansible

[Ansible](https://www.ansible.com/) is an open-source tool for server
configuration. It simplifies automation in an environment with multiple
servers. Ansible only needs to be installed on the machine you use for setting
up the cluster (it does not need to run on the RPis). A more detailed
documentation can be found [here](https://docs.ansible.com).


Installing Ansible depends on the operating system running on your
machine. For instance, for Ubuntu 18.04, it works as follows (most Linux
distributions come with a package for Ansible):

```bash
sudo apt update
sudo apt install software-properties-common
sudo apt-add-repository ppa:ansible/ansible
sudo apt update
sudo apt install ansible
```

Now that Ansible is installed, you need to accept the ssh keys of all
the RPis. This can be done by opening an ssh connection to every RPi

```bash
# ssh connection (or add fingerprints)
ssh pi@10.42.0.250
ssh pi@10.42.0.251
ssh pi@10.42.0.252
ssh pi@10.42.0.253
```

Last but not least, you may need to adapt the inventory.ini to your
configuration. It contains a list of all RPis, allows the specification of
groups and much more.

```bash
# edit inventory.ini and add all servers you want to connect to
rpi0 ansible_host=10.42.0.250 ansible_user=pi ansible_ssh_pass=raspberry
rpi1 ansible_host=10.42.0.251 ansible_user=pi ansible_ssh_pass=raspberry
rpi2 ansible_host=10.42.0.252 ansible_user=pi ansible_ssh_pass=raspberry
rpi3 ansible_host=10.42.0.253 ansible_user=pi ansible_ssh_pass=raspberry
...
```

The RPi "rpi0" will be used as swarm/cluster manager, the RPis "rpi1", "rpi2",
and "rpi3" will be configured as workers.


## Trying out Ansible

You can try out some basic ansible commands on your machine just to see how it
works, e.g. pinging all RPis, running some shell command, and rebooting or
shutting down the RPis:


```bash
# now we can ping all servers with ansible
ansible all -m ping -i inventory.ini

# or run some shell commands
ansible all -m shell -a "hostname"
ansible all -m shell -a "df -h"

# or reboot
ansible all -m reboot --become -i inventory.ini

# or shutdown
ansible all -m shell -a "sudo shutdown now" --become -i inventory.ini 
```


## Ansible Playbooks

Ansible Playbooks are comparable to bash-scripts with some additional
features. They simplify running a list of commands, such as "apt install", on
many servers simultaneously.

This directory "Ansible" contains the following Playbooks:

- utilities.yaml
  --> Installs basic tools such as vim, nmap and git
- docker.yaml
  --> Installs docker + docker-compose  using the installation script (only RPi)
- swarm.yaml
  --> (Re-)installs and (re-)initializes Docker Swarm + GlusterFS based on the groups [docker_swarm_manager] and [docker_swarm_workers] in the inventory.ini


Running the Playbooks is straightforward. Just follow the instructions below:

```bash
# install utilities such as vim/git
ansible-playbook utilities.yaml -i inventory.ini
# install Docker
ansible-playbook docker.yaml -i inventory.ini
# initializes Docker Swarm + GlusterFS
ansible-playbook swarm.yaml -i inventory.ini
```

Please note that RPis are not high-performance computers, so some scripts may
take some time to run (10-15 minutes). Also, RPis are not the
most stable platforms, which means that the scripts may fail, e.g. by timing
out or returning with a failed state for one or more RPis. If this happens,
just rerun the script. In case a Raspberry Pi does not reboot correctly,
disconnect/reconnect power and wait for Ansible to finish (and the RPi to
finish rebooting).  Then rerun the playbook.


If it still does not work, reconfigure the RPi (or RPIs) that caused the
problems by starting from scratch, i.e., flashing the Raspbian operating
system and going through all the steps in "RPiSetup".



## Service Deployment (Visualizer, Spark, JupyterLab)

We now deploy various services on the cluster: a visualizer to monitor the
(current) setup of the cluster, Spark (a big-data analytics platform), and
JupyterLab (to run Jupyter notebooks). An instructional video is
available. Please check the text below, though, as the video uses different
parameters.


<div align="center">
  <a href="https://www.youtube.com/watch?v=Tj-Rb9JvQ7w">
    <img src="images/deployment.png" alt="PiCluster Service Deployment" style="width:30%;">
  </a>
</div>

In order to deploy a service on your cluster, you **use ssh and
connect to your master node** (10.42.0.250), as services cannot be deployed on
worker nodes. First, we deploy a monitoring tool called
**Visualizer** as shown below. Because of the port is mapped to the outside
(--publish), you can directly access the Visualizer from any browser (visit
http://10.42.0.250:80).


```bash
# deploy Visualizer on port 80 and constrain it to the master
docker service create --name=viz --publish=80:8080/tcp --constraint=node.role==manager --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock alexellis2/visualizer-arm:latest

# kill the visualizer if needed
docker service rm viz
```


Next we deploy **Spark** using the commands below.  Adjust the parameters
(e.g. --replicas 4) to your needs. The Spark UI can be accessed on port 8080
(visit http://10.42.0.250:8080). The following command, creating an overlay
network, will probably return with an error, as the network has already been
created earlier. 


```bash
# create an attachable overlay network
# (all spark containers have to be within the same network to be able to connect)
docker network create -d overlay --attachable spark
```

If the command above returns with the following error message, everything is
fine. Just continue with the installation.

```bash
Error response from daemon: network with name spark already exists 
```

We now install the Spark master in the first step and the workers in a
second step.

```bash
# run spark master
# (the first run might take about 10 minutes because it has to download the image on all RPis)
docker service create --name sparkmaster --network spark --constraint=node.role==manager --publish 8080:8080 --publish 7077:7077 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.master.Master
```

```bash
# run spark workers
# (runs four workers and mounts gluster at /gfs to synchronize files accross all nodes)
docker service create --replicas 4 --replicas-max-per-node 1 --name sparkworker --network spark --publish 8081:8081 --mount source=gfs,destination=/gfs pgigeruzh/spark:arm bin/spark-class org.apache.spark.deploy.worker.Worker spark://sparkmaster:7077
```

Last but not least, we deploy JupyterLab on port 8888 as below (visit
http://10.42.0.250:8888 to access).

```bash
# run jupyter lab
# (constraint to the manager because it mounts the docker socket)
docker service create --name jupyterlab --network spark --constraint=node.role==manager --publish 8888:8888 --mount source=gfs,destination=/gfs --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock -e SHELL=/bin/bash pgigeruzh/spark:arm jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password='' --notebook-dir='/gfs'
```

In summary, you should have the following services up and running.

| Service    | URL              |
| ---------- | ---------------- |
| Visualizer | 10.42.0.250:80   |
| Spark UI   | 10.42.0.250:8080 |
| JupyterLab | 10.42.0.250:8888 |



For managing the cluster, the following commands may be useful:

```bash
# list all services
docker service ls

# remove a service
docker service rm your-service-name
```

