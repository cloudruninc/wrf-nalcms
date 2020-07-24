import argparse


def cli():
    parser = argparse.ArgumentParser(description='nalcms - Process NALCMS land use data for ingestion into WRF')
    args = parser.parse_args()
