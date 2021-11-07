import os
import time

from digitalocean import Droplet, Manager
from fabric import task

DIGITAL_OCEAN_ACCESS_TOKEN = os.getenv("DIGITAL_OCEAN_ACCESS_TOKEN")
user = "root"
hosts = []


# tasks


@task
def ping(ctx, output):
    """Sanity check"""
    print("pong!")
    print(f"hello {output}!")


@task
def create_droplets(ctx):
    """
    Create three new DigitalOcean droplets -
    node-1, node-2, node-3
    """
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    all_keys = manager.get_all_sshkeys()
    keys = []
    for key in all_keys:
        if "Nina" in key.name:
            keys.append(key)
    for num in range(3):
        node = f"node-{num + 1}"
        droplet = Droplet(
                token=DIGITAL_OCEAN_ACCESS_TOKEN,
                name=node,
                region="nyc3",
                image="ubuntu-20-04-x64",
                size="s-2vcpu-4gb",
                tags=[node],
                ssh_keys=keys,
                )
        droplet.create()
        print(f"{node} has been created.")

@task
def wait_for_droplets(ctx):
    """Wait for each droplet to be ready and active"""
    for num in range(3):
        node = f"node-{num + 1}"
        while True:
            status = get_droplet_status(node)
            if status == "active":
                print(f"{node} is ready.")
                break
            else:
                print(f"{node} is not ready.")
                time.sleep(5)


def get_droplet_status(node):
    """Given a droplet's tag name, return the status of the droplet"""
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    droplet = manager.get_all_droplets(tag_name=node)
    return droplet[0].status

@task
def destroy_droplets(ctx):
    """Destroy the droplets - node-1, node-2, node-3"""
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    for num in range(3):
        node = f"node-{num + 1}"
        droplets = manager.get_all_droplets(tag_name=node)
        for droplet in droplets:
            droplet.destroy()
        print(f"{node} has been destroyed.")

@task
def get_addresses(ctx, type):
    """Get IP address"""
    manager = Manager(token=DIGITAL_OCEAN_ACCESS_TOKEN)
    if type == "master":
        droplet = manager.get_all_droplets(tag_name="node-1")
        print(droplet[0].ip_address)
        hosts.append(droplet[0].ip_address)
    elif type == "workers":
        for num in range(2, 4):
            node = f"node-{num}"
            droplet = manager.get_all_droplets(tag_name=node)
            print(droplet[0].ip_address)
            hosts.append(droplet[0].ip_address)
    elif type == "all":
        for num in range(3):
            node = f"node-{num + 1}"
            droplet = manager.get_all_droplets(tag_name=node)
            print(droplet[0].ip_address)
            hosts.append(droplet[0].ip_address)
    else:
        print('The "type" should be either "master", "workers", or "all".')
    print(f"Host addresses - {hosts}")
