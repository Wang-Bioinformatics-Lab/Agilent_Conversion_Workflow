import sys
import argparse
import pandas as pd

def convert_agilent(input_filename, output_filename, msconvert_bin):
    scan_current = 1
    previous_ms1_scan = 0

    temp_mzML = os.path.join(os.path.dirname(output_filename), "{}.mzML".format(str(uuid.uuid4())))

    with MzMLWriter(open(temp_mzML, 'wb'), close=True) as out:
        # Add default controlled vocabularies
        out.controlled_vocabularies()
        # Open the run and spectrum list sections
        with out.run(id="my_analysis"):
            with out.spectrum_list(count=1):
                #spectrum_count = len(scans) + sum([len(products) for _, products in scans])
                run = pymzml.run.Reader(input_filename)
                for spectrum in run:
                    if spectrum['ms level'] == 1:
                        out.write_spectrum(
                            spectrum.mz, spectrum.i,
                            id="scan={}".format(scan_current), params=[
                                "MS1 Spectrum",
                                {"ms level": 1},
                                {"total ion current": sum(spectrum.i)}
                            ],
                            scan_start_time=spectrum.scan_time_in_minutes())
                        previous_ms1_scan = scan_current
                        scan_current += 1
                    elif spectrum["ms level"] == 2:
                        precursor_spectrum = spectrum.selected_precursors[0]
                        precursor_mz = precursor_spectrum["mz"]
                        precursor_intensity = 0
                        precursor_charge = 0

                        try:
                            precursor_charge = precursor_spectrum["charge"]
                            precursor_intensity = precursor_spectrum["i"]
                        except:
                            pass

                        out.write_spectrum(
                            spectrum.mz, spectrum.i,
                            id="scan={}".format(scan_current), params=[
                                "MS1 Spectrum",
                                {"ms level": 2},
                                {"total ion current": sum(spectrum.i)}
                            ],
                            # Include precursor information
                            precursor_information={
                                "mz": precursor_mz,
                                "intensity": precursor_intensity,
                                "charge": precursor_charge,
                                "scan_id": "scan={}".format(previous_ms1_scan),
                                "activation": ["beam-type collisional dissociation", {"collision energy": spectrum["collision energy"]}]
                            },
                            scan_start_time=spectrum.scan_time_in_minutes())

                        scan_current += 1

    # Reconvert with msconvert
    cmd = '{} {} --32 --zlib --ignoreUnknownInstrumentError \
        --outdir {} --outfile {}'.format(msconvert_bin, temp_mzML, os.path.dirname(output_filename), os.path.basename(output_filename))
    print(cmd)
    os.system(cmd)


def main():
    parser = argparse.ArgumentParser(description='Test write out a file.')
    parser.add_argument('input_filename')
    parser.add_argument('output_filename')
    parser.add_argument('--msconvert_bin', default='msconvert')

    args = parser.parse_args()

    convert_agilent(args.input_filename, args.output_filename, msconvert_bin)



if __name__ == "__main__":
    main()