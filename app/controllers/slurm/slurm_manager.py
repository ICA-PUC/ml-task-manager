from ...config import settings
"""Slurm Job Manager for job instanciation controll"""
from ...utils import save_file, strip_filename


def read_template(template_path):
    """read template file"""
    with open(template_path, "r", encoding='utf-8') as f:
        template = f.read()
    return template


def prepare_srm_template(task_dict):
    """Prepare srm template with task_dict"""
    if "atena" in task_dict['runner_location']:
        template = read_template("app/controllers/slurm/slurm_template.srm")
    elif "dev" in task_dict['runner_location']:
        template = read_template("app/controllers/slurm/dev_template.srm")
    slurm_script = template.format(
        experiment_name=task_dict['experiment_name'],
        instance_type=task_dict['instance_type'],
        account=task_dict['account'],
        image_name=task_dict['image_name'],
        script_name=strip_filename(task_dict['script_path']),
        dataset_name=task_dict['dataset_name'],
        task_id=task_dict['id'],
        sif_path = settings.sif_root,
        atena_root = settings.atena_root,
        nfs_root = settings.nfs_root,
    )
    fname = f'slurm_script_{task_dict["id"]}.srm'
    fpath = save_file(fname, slurm_script,task_dict["id"])
    return fname
