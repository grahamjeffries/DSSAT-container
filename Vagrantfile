# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  # Vagrant base box
  config.vm.box = "ubuntu/trusty64"

  # workaround for 'stdin: is not a tty' error per discussion at https://github.com/mitchellh/vagrant/issues/1673
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  # forward ssh credientials to authorize git requests
  config.ssh.forward_agent = true

  # Basic provisioning
  # TODO: convert to Ansible
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update -qq
    sudo apt-get upgrade -y -qq
    sudo apt-get install gfortran git -y -qq

    ssh-keyscan github.com >> ~/.ssh/known_hosts

    cd /vagrant
    git clone git@github.com:grahamjeffries/dssat-csm.git
    python prepare_dssat.py

    make clean
    make

  SHELL
end


