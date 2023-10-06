#!/usr/bin/env nextflow
nextflow.enable.dsl=2

params.input_spectra_folder = ""

TOOL_FOLDER = "$baseDir/bin"

process renumberSpectra {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    file input_mzML 

    output:
    file 'converted/*.mzML'

    """
    mkdir converted
    python $TOOL_FOLDER/convert_agilent.py $input_mzML converted/$input_mzML
    """
}

workflow {
    data = Channel.fromPath(params.input_spectra_folder + "/*.mzML")
    
    // Outputting Python
    renumberSpectra(data)
}