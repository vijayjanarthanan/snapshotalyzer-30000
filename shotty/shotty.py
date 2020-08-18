import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances=[]
    if project:
        filters = [{'Name':'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances;

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands related to snapshots"""

@snapshots.command("list")
@click.option("--project", default=None,
    help="Only snapshots for project (tag Project:<name>)")
def listSnapshots(project):
    "List of Snapshots"
    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print (
                    ", ".join((
                        s.id,
                        v.id,
                        i.id,
                        s.state,
                        s.progress,
                        s.start_time.strftime("%c")
                    )))
    return

@cli.group('volumes')
def volumes():
    """Commands related to volumes"""

@volumes.command('list')
@click.option("--project", default=None,
    help="Only volumes for project (tag Project:<name>)")
def listVolumes(project):
    "List of volumes for each EC2 instance"
    instances = filter_instances(project)

    for i in instances:
        for vol in i.volumes.all():
            print (", ".join((
                vol.id,
                i.id,
                vol.state,
                str(vol.size) + "GiB",
                vol.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return

@cli.group()
def instances():
    """Commands related to instances"""

@instances.command('createSnapshot')
@click.option("--project", default=None,
    help="Only instances for project (tag Project:<name>)")
def createSnapshot(project):
    "Creates snaphots of all volumes for all instances in a given project"
    instances = filter_instances(project)

    for inst in instances:
        print("Stopping instance {0}".format(inst.id))
        inst.stop()
        inst.wait_until_stopped()

        for vol in inst.volumes.all():
            print ("    Creating snapshot of {0}".format(vol.id))
            vol.create_snapshot(Description="Created by Snapshotalyzer")

        print("Starting instance {0}".format(inst.id))
        inst.start()
        inst.wait_until_running()

    print("Snapshots created for all volumes and instances restarted.")
    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def listInstances(project):
    "List of EC2 Instances"

    instances = filter_instances(project)

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

    instances = filter_instances(project)
    for inst in instances:
        print("Stopping instance " + str(inst.id) + "...")
        inst.stop()
    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def listInstances(project):
    "Start EC2 Instances"

    instances = filter_instances(project)
    for inst in instances:
        print("Starting instance " + str(inst.id) + "...")
        inst.start()
    return

if __name__ == '__main__':
    cli()
