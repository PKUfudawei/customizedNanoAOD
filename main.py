#!/usr/bin/env python3
import os, sys, argparse


def parse_commandline():
    parser = argparse.ArgumentParser(description='Script to generate customized NanoAOD')
    parser.add_argument('-f', '--file', help='To specify file path')
    parser.add_argument('-o', '--outdir', help='To specify output directory', default='$HOME')
    parser.add_argument('-y', '--year', help='To specify which year', choices=('2016pre', '2016post', '2017', '2018'))
    parser.add_argument('-t', '--type', help='To specify which sample type', choices=('mc', 'data'))
    args = parser.parse_args()
    return args


def produce_custom_nanoaod(file: str, year: str, sample_type: str, outdir: str):
    mode = f'{sample_type}_{year}'
    filetype = 'NANOAODSIM' if sample_type == 'mc' else 'NANOAOD'
    MODE = 'MC' if sample_type == 'mc' else 'Data'
    condition = {
        'mc_2016pre': '106X_mcRun2_asymptotic_preVFP_v9',
        'mc_2016post': '106X_mcRun2_asymptotic_v15',
        'mc_2017': '106X_mc2017_realistic_v8',
        'mc_2018': '106X_upgrade2018_realistic_v15_L1v1',
        'data_2016pre': '106X_dataRun2_v32',
        'data_2016post': '106X_dataRun2_v32',
        'data_2017': '106X_dataRun2_v32',
        'data_2018': '106X_dataRun2_v32',
    }
    outfile = os.path.join(outdir, 'custom_nano.root')
    
    if file.startswith('root://'):
        os.system(f"source /cvmfs/cms.cern.ch/cmsset_default.sh; xrdcp {file} .")
        file = os.path.join('$HOME', file.split('/')[-1])
    
    os.system(rf"""
    source /cvmfs/cms.cern.ch/cmsset_default.sh
    export HOME=`pwd`; export SCRAM_ARCH=slc7_amd64_gcc700
    rm -rf CMSSW_10_6_30/; cmsrel CMSSW_10_6_30; cd CMSSW_10_6_30/src; eval `scram runtime -sh`; cmsenv
    git clone https://github.com/gqlcms/Customized_NanoAOD.git .
    ./PhysicsTools/NanoTuples/scripts/install_onnxruntime.sh; scram b -j 16

    cmsDriver.py {mode} -n -1 --{sample_type} --eventcontent {filetype} --datatier {filetype} \
        --conditions {condition[mode]} --step NANO --nThreads 1 --era Run2_{year[:4]},run2_nanoAOD_106Xv1 \
        --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customize{MODE} \
        --filein file:{file} --fileout file:{outfile} --no_exec;

    cmsRun {mode}_NANO.py
    """)
    

def main():
    if len(sys.argv) < 3:
        raise ValueError('miniAODToCustomNanoAOD.py needs three necessary arguments as file, year and type by -f, -y and -t respectively')
    args = parse_commandline()
    produce_custom_nanoaod(file=args.file, year=args.year, sample_type=args.type, outdir=args.outdir)


if __name__ == "__main__":
    main()
