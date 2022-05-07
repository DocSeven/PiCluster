# A Raspberry Pi Cluster for Teaching/Experimentation

This repo contains the following:

| Directory  | Description                                                                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| RPiSetup   | Doing the basic set-up of the Raspberry Pi devices from scratch. |
| Ansible    | Ansible scripts to automate the setup of the cluster. You only need Ansible and an SSH connection to all RPis. |
| Exercises  | Python (PySpark) exercises for a lecture/module.|
| Doc        | Some additional documentation for setting up other frameworks on the cluster.|                                                                           
| Benchmarks | A description of benchmarks used to test the cluster. Some experimental data and analysis can also be found here.   |


The order of the directories in the table above reflect the order which you
have to follow to set up the cluster, i.e., start with "RPiSetup", then go on
to "Ansible", and take your cluster for a first spin with "Exercises". The
final two directories contain some additional material.


A big thanks goes out to Peter Giger, Sajan Srikugan, and Badrie L. Persaud,
who have done the essential work to get the cluster up and running in their
MSc project at the University of Zurich.

