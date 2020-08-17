import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def list_instances(project):
    instances=[]
    if project:
        filters = [{'Name':'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances;

@click.group()
def instances():
    """Commands realted to EC2 instances"""

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def listInstances(project):
    "List of EC2 Instances"

    instances = list_instances(project)

    for inst in instances:
        tags = { tag['Key'] : tag['Value'] for tag in inst.tags or [] }
        print(', '.join((
            inst.id,
            inst.instance_type,
            inst.placement['AvailabilityZone'],
            inst.state['Name'],
            inst.public_dns_name or "<no dns name>",
            tags.get('Project','<no project>')
            )))
    return


@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def listInstances(project):
    "Stop EC2 Instances"

    instances = list_instances(project)
    for inst in instances:
        print("Stopping instance " + str(inst.id) + "...")
        inst.stop()
    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def listInstances(project):
    "Start EC2 Instances"

    instances = list_instances(project)
    for inst in instances:
        print("Starting instance " + str(inst.id) + "...")
        inst.start()
    return

if __name__ == '__main__':
    instances()
