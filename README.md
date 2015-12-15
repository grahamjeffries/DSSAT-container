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
Launch the vagrant instance and DSSAT model will be built
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

## Dependencies
- Vagrant (and thus VirtualBox)
- Access to the DSSAT source code on GitHub
