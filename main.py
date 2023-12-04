import gradio as gr
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import ants

def flipQMT(sub_id, img1, img2):

    # Load NIfTI images
    psr = nib.load(img1.name)
    r1f = nib.load(img2.name)
    psr_d = psr.get_fdata()
    r1f_d = r1f.get_fdata()

    output_path1 = f"{sub_id}_PSR_flip.nii"
    output_path2 = f"{sub_id}_R1F_flip.nii"

    nib.Nifti1Image(np.flip(psr_d, 0), psr.affine).to_filename(output_path1)
    nib.Nifti1Image(np.flip(r1f_d, 0), r1f.affine).to_filename(output_path2)
    return [output_path1, output_path2]

def modifyQMT(sub_id, file1, file2, file3):
    # Load NIfTI images
    fixed = ants.image_read(file1.name)
    psr = ants.image_read(file2.name)
    r1f = ants.image_read(file3.name)

    mytx = ants.registration(fixed=fixed, moving=psr, type_of_transform='Rigid', verbose=True)
    mv_psr = mytx['warpedmovout']

    output_path1 = f"{sub_id}_PSR_correct.nii"
    output_path2 = f"{sub_id}_R1F_correct.nii"

    ants.image_write(mv_psr, output_path1)
    mv_r1f = ants.apply_transforms(fixed=fixed, moving=r1f,
                                   transformlist=mytx['fwdtransforms'])
    ants.image_write(mv_r1f, output_path2)

    return [output_path1, output_path2]

def registerLongi(sub_id, file1, file2, file3, file4, file5, file6, file7, choice):
    # Load NIfTI images
    fixed = ants.image_read(file1.name)

    flair = ants.image_read(file2.name)
    swi = ants.image_read(file3.name)
    phase = ants.image_read(file4.name)
    fswi = ants.image_read(file5.name)
    psr = ants.image_read(file6.name)
    r1f = ants.image_read(file7.name)

    mytx = ants.registration(fixed=fixed, moving=flair, type_of_transform='Rigid', verbose=True)
    mv_flair = mytx['warpedmovout']
    mv_swi = ants.apply_transforms(fixed=fixed, moving=swi,
                                   transformlist=mytx['fwdtransforms'])
    mv_phase = ants.apply_transforms(fixed=fixed, moving=phase,
                                   transformlist=mytx['fwdtransforms'])
    mv_fswi = ants.apply_transforms(fixed=fixed, moving=fswi,
                                   transformlist=mytx['fwdtransforms'])
    mv_psr = ants.apply_transforms(fixed=fixed, moving=psr,
                                   transformlist=mytx['fwdtransforms'])
    mv_r1f = ants.apply_transforms(fixed=fixed, moving=r1f,
                                   transformlist=mytx['fwdtransforms'])

    output_path1 = f"{choice}_{sub_id}_flair_reg_Baseline.nii"
    output_path2 = f"{choice}_{sub_id}_swi_reg_Baseline.nii"
    output_path3 = f"{choice}_{sub_id}_phase_reg_Baseline.nii"
    output_path4 = f"{choice}_{sub_id}_fair-swi_reg_Baseline.nii"
    output_path5 = f"{choice}_{sub_id}_psr_reg_Baseline.nii"
    output_path6 = f"{choice}_{sub_id}_r1f_reg_Baseline.nii"

    ants.image_write(mv_flair, output_path1)
    ants.image_write(mv_swi, output_path2)
    ants.image_write(mv_phase, output_path3)
    ants.image_write(mv_fswi, output_path4)
    ants.image_write(mv_psr, output_path5)
    ants.image_write(mv_r1f, output_path6)

    return [output_path1, output_path2, output_path3, output_path4, output_path5, output_path6]


# Create a single Blocks instance
with gr.Blocks() as app:
    gr.Markdown("<center><h1>post Processing to multi-modalities of MS MR sequences for Longitudinal Research</h1></center>")

    # Markdown with hyperlink and icon
    gr.Markdown("This work is the toolbox to pross MS mutliple different sequence including flair/swi and qMT-PSR and R1F. <br>"
                "It is written by Jiacheng Wang from [MedICL](https://github.com/MedICL-VU) and [Bagnato Lab](https://www.vumc.org/bagnato-lab/our-mission) at Vanderbilt University and VUMC. <br>"
                "For more questions, please contact [Jiacheng Wang](https://jackywang22.github.io/). ")

    with gr.Tab('Prepare qMT in SWI space'):
        gr.Markdown("### We need to flip the PSR/R1F Image to have the right orientation")
        sub_id = gr.Textbox(label="Enter Subject ID")
        with gr.Row():
            file1 = gr.File(label="Upload PSR")
            file2 = gr.File(label="Upload R1F")
            output_files = gr.Files(label="Download Image(s)")
        gr.Button("Process").click(flipQMT, inputs=[sub_id, file1, file2], outputs=output_files)

        gr.Markdown("### Make the qMT (PSR/R1F) to have correct slice number as SWI space")
        with gr.Row():
            file3 = gr.File(label="Upload FLAIR image in SWI space (w/ skullStrip)")
            file4 = gr.File(label="Upload flipped- PSR Image")
            file5 = gr.File(label="Upload flipped- R1F Image")
            output_files = gr.Files(label="Download Image(s)")
        gr.Button("Process").click(modifyQMT, inputs=[sub_id, file3, file4, file5], outputs=output_files)

    with gr.Tab('Longitudinal Registration'):
        gr.Markdown("### Please provide the Baseline FLAIR image (w/o skullstrip)")
        b_flair = gr.File(label="Upload Baseline FLAIR")

        choice = gr.Radio(["Year1", "Year2", "Year3"], label="Select longitudinal year")
        new_sub_id = gr.Textbox(label="Enter longitudinal Subject ID")
        with gr.Row():
            flair = gr.File(label="Upload FLAIR w/o skullstrip")
            swi = gr.File(label="Upload SWI")
            phase = gr.File(label="Upload Phase")
            fswi = gr.File(label="Upload FLAIR-SWI")
            psr = gr.File(label="Upload PSR")
            r1f = gr.File(label="Upload R1F")

        output_files = gr.Files(label="Download Image(s)")
        gr.Button("Process").click(registerLongi, inputs=[new_sub_id, b_flair, flair, swi, phase, fswi, psr, r1f, choice], outputs=output_files)
# Run the app
app.launch()
