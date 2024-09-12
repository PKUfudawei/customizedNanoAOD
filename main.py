#!/usr/bin/env python3
import os, sys, argparse


def parse_commandline():
    parser = argparse.ArgumentParser(description='Script to generate customized NanoAOD')
    parser.add_argument('-f', '--file', help='To specify file path', default=None)
    parser.add_argument('-o', '--outdir', help='To specify output directory', default='$HOME')
    parser.add_argument('-m', '--mode', help='To specify $type_$year_$channel mode', default='mc_2018_ZpToHG')
    args = parser.parse_args()
    return args


def produce_custom_nanoaod(file: str, year: str, sample_type: str, outdir: str='./'):
    mode = f'{sample_type}_{year}'
    filetype = 'NANOAODSIM' if sample_type == 'mc' else 'NANOAOD'
    MODE = 'MC' if sample_type == 'mc' else 'Data'
    condition = {  # https://twiki.cern.ch/twiki/bin/view/CMSPublic/GTsAfter2019
        'mc_2016pre': '106X_mcRun2_asymptotic_preVFP_v11',
        'mc_2016post': '106X_mcRun2_asymptotic_v17',
        'mc_2017': '106X_mc2017_realistic_v9',
        'mc_2018': '106X_upgrade2018_realistic_v16_L1v1',
        'data_2016pre': '106X_dataRun2_v37',
        'data_2016post': '106X_dataRun2_v37',
        'data_2017': '106X_dataRun2_v37',
        'data_2018': '106X_dataRun2_v37',
    }
    outfile = os.path.join(outdir, 'custom_nano.root')
    os.system(rf"""
    source /cvmfs/cms.cern.ch/cmsset_default.sh
    export HOME=`pwd`; export SCRAM_ARCH=slc7_amd64_gcc700
    rm -rf CMSSW_10_6_31; scram p CMSSW CMSSW_10_6_31; cd CMSSW_10_6_31/src; eval `scram runtime -sh`; cmsenv
    git clone https://github.com/colizz/NanoTuples.git PhysicsTools/NanoTuples -b dev-part-UL
    ./PhysicsTools/NanoTuples/scripts/install_onnxruntime.sh
    wget https://coli.web.cern.ch/coli/tmp/.240120-181907_ak8_stage2/model.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoTuples/data/InclParticleTransformer-MD/ak8/V02/model.onnx
    scram b clean && scram b -j4; cd ~

    cmsDriver.py {mode} -n -1 --{sample_type} --eventcontent {filetype} --datatier {filetype} \
        --conditions {condition[mode]} --step NANO --nThreads 1 --era Run2_{year[:4]},run2_nanoAOD_106Xv2 \
        --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customize{MODE} \
        --filein file:{file} --fileout file:{outfile} --no_exec;

    cmsRun {mode}_NANO.py
    """)
    

def main():
    if len(sys.argv) < 3:
        raise ValueError('produce_custom_nanoaod() needs two necessary arguments as file, year and type by -f, -y and -t respectively')
    args = parse_commandline()
    file = args.file
    if file.startswith('root://'):
        os.system(f"xrdcp {file} .")
        file = file.split('/')[-1]
    sample_type, year, channel = args.mode.split('_')
    produce_custom_nanoaod(file=file, year=year, sample_type=sample_type, outdir=args.outdir)


if __name__ == "__main__":
    main()
