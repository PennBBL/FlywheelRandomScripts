# sometimes, Flywheel fails to classify dicoms, meaning that dcm2niix doesn't run and subsequent niftis aren't produced. 
# This script goes through a Flywheel project and checks each acquisition for both a dicom and a nifti. If there's no nifti present,
# it launches dcm2niix on the acquisition dicom.

# the only argument is the project label

# python dcm2niix_fw.py MY_PROJECT

import flywheel
import sys

client = flywheel.Client()

project_label = sys.argv[1]
project_obj = client.projects.find_first('label="{}"'.format(project_label))

sessions = client.get_project_sessions(project_obj.id)

dcm2nif = client.get_gear("5cb92ec53767f900271bbc92")
inputs = list(dcm2nif.gear.inputs.keys())

jobs = []

for i,s in enumerate(sessions):
    print("Ses ", s.label)
    acqs=s.acquisitions()
    for j,a in enumerate(acqs):
        files=a.files
        types=[x.type for x in files]
        # dicomFile = [f for f in a.files if f['type'] == "dicom"][0]
        if ('dicom' in types) and ('nifti' not in types):
            print("Acq ", j, ": No nifti here")

            dcm = [f for f in a.files if f['type'] == "dicom"][0]
            if dcm:
                print("converting")
                dcm_input = {inputs[0]: a.get_file(dcm.name)}
                jobID = dcm2nif.run(inputs=dcm_input, destination=a)

                jobs.append(jobID)

        else:
            print("Acq ", s.label, " OK")
