#!/usr/bin/env python3
import argparse
import os
import glob


def parse_commandline():
    parser = argparse.ArgumentParser(description='Script to check if each condor job is done')
    parser.add_argument('-t', '--type', help='To specify jobs in mc/ or data/', choices=('data', 'mc', '*'), default='*')
    parser.add_argument('-y', '--year', help='To specify jobs in which year', default='*')
    parser.add_argument('-c', '--channel', help='To specify jobs in which channel', default='*')
    parser.add_argument('-j', '--job', help='Specify which job to be submitted', default='*')
    args = parser.parse_args()
    return args


def main():
    args = parse_commandline()
    os.system('condor_status -schedd')
    os.system("which condor_submit")
    input("====> Are you ready to submit condor jobs?")

    os.system("rm -rf log/*/*/*/*/*")
    os.system(f"""
        for jdl in submit/{args.type}/{args.year}/{args.channel}/{args.job}.submit
            do condor_submit $jdl
        done
    """)

   
if __name__ == "__main__":
    main()
