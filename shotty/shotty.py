import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.command()
def listInstances():
    "List of EC2 Instances"
    for inst in ec2.instances.all():
        print(', '.join((
            inst.id,
            inst.instance_type,
            inst.placement['AvailabilityZone'],
            inst.state['Name'],
            inst.public_dns_name)))
    return

if __name__ == '__main__':
    listInstances()
