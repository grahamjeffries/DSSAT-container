## DSSAT-container

DSSAT-container is virtual environment for the DSSAT modeling suite designed to simplify and modernize user-model interactions. Vagrant is used in the project to create portable, replicable working environments to faciliate collaborative modeling and improve the reproducability of scientific research conducted with DSSAT.

Currently, the project requires that you have access to the DSSAT source code on GitHub. See the Dependencies below.

## Getting started
Clone the repo
```
git clone git@github.com:grahamjeffries/DSSAT-container.git
```
Move into the project directory
```
cd DSSAT-container
```
To allow the Vagrant instance to clone private git repositories you have access to, your ssh private key must be available to the local ssh-agent. You can check with ```ssh-add -L```. If it's not listed add it with ```ssh-add <path to key, e.g. ~/.ssh/id_rsa>```
Launch the Vagrant instance and DSSAT model will be built
```
vagrant up
```
Enter the Vagrant virtual machine and move to the directory where the model is located
```
vagrant ssh
```
```
cd /vagrant/DSSAT46
```
Then you can run the model
```
./DSCSM046.EXE A <your experiment file>
```

## Notes
Currently the Vagrantfile clones a fork of the main DSSAT repository. The fork introduces bug fixes which are required for *NIX systems but are not presently in the main repo.

## Dependencies
- Vagrant (and thus VirtualBox)
- Access to the DSSAT source code on GitHub

