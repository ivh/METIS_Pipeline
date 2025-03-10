from edps import SCIENCE, QC1_CALIB, QC0, CALCHECKER
from edps import task, subworkflow, qc1calib, match_rules, FilterMode, calchecker
from .metis_datasources import *
from . import metis_keywords as metis_kwd


dark_task = (task('metis_det_dark')
            .with_main_input(raw_dark)
            .with_recipe("metis_det_dark")
            .build())

lingain_task = (task('metis_det_detlin')
                .with_recipe("metis_det_lingain")
                .with_main_input(detlin_2rg_raw)
                .with_associated_input(dark_task)
                .with_associated_input(lm_wcu_off_raw)
                .build())

flat_task = (task("metis_lm_img_flat")
             .with_main_input(lm_lamp_flat)
             .with_associated_input(dark_task)
             .with_associated_input(lingain_task)
             .with_recipe("metis_lm_img_flat")
             .build())

distortion_task = (task('metis_lm_img_cal_distortion')
                   .with_main_input(lm_distortion_raw)
                   .with_associated_input(lm_wcu_off_raw)
                   .with_associated_input(pinehole_tab)
                   .with_associated_input(lingain_task)
                   .with_recipe('metis_lm_img_distortion')
                   .build())

basic_reduction_sci = (task('metis_lm_img_basic_reduce_sci')
                    .with_recipe('metis_lm_img_basic_reduce')
                    .with_main_input(lm_raw_science)
                    .with_associated_input(lingain_task)
                    .with_associated_input(dark_task)
                    .with_associated_input(flat_task)
                    .with_meta_targets([SCIENCE])
                    .build())

basic_reduction_sky = (task('metis_lm_img_basic_reduce_sky')
                    .with_recipe('metis_lm_img_basic_reduce')
                    .with_main_input(lm_raw_sky)
                    .with_associated_input(lingain_task)
                    .with_associated_input(dark_task)
                    .with_associated_input(flat_task)
                    .with_meta_targets([SCIENCE])
                    .build())

basic_reduction_std = (task('metis_lm_img_basic_reduce_std')
                    .with_recipe('metis_lm_img_basic_reduce')
                    .with_main_input(lm_raw_std)
                    .with_associated_input(lingain_task)
                    .with_associated_input(dark_task)
                    .with_associated_input(flat_task)
                    .with_meta_targets([SCIENCE])
                    .build())

background_sci_task = (task('metis_lm_img_background_sci')
                    .with_recipe('metis_lm_img_background')
                    .with_main_input(basic_reduction_sci)
                    .with_associated_input(basic_reduction_sky)
                    .with_meta_targets([SCIENCE])
                    .build())

background_std_task = (task('metis_lm_img_background_std')
                    .with_recipe('metis_lm_img_background')
                    .with_main_input(basic_reduction_std)
                    .with_associated_input(basic_reduction_sky)
                    .with_meta_targets([SCIENCE])
                    .build())

standard_flux_task = (task('metis_lm_img_standard_flux')
                    .with_recipe('metis_lm_img_std_process')
                    .with_main_input(background_std_task)
                    .with_associated_input(fluxstd_catalog)
                    .with_meta_targets([SCIENCE])
                    .build())

img_calib = (task('metis_lm_img_calib')
             .with_recipe('metis_lm_img_calibrate')
             .with_main_input(background_sci_task)
             .with_associated_input(standard_flux_task)
             .with_associated_input(distortion_task)
             .with_meta_targets([SCIENCE])
             .build())
             
img_coadd = (task('metis_lm_img_coadd')
             .with_recipe('metis_lm_img_sci_postprocess')
             .with_main_input(img_calib)
             .with_meta_targets([SCIENCE])
             .build())
# QC1