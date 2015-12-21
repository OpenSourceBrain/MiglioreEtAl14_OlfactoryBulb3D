# Launch this with "python customsim.py 2 10"
# to get a network with 2 Mitral cells and 10 Granule cells/Mitral (20 total)

if __name__ == '__main__':

    import sys
    import custom_params
    custom_params.filename = 'fig7'

    if len(sys.argv) > 1:
        custom_params.customMitralCount = int(sys.argv[1])
        custom_params.customGranulesPerMitralCount = int(sys.argv[2])

    import params
    import runsim
    runsim.build_complete_model('c10.dic')
    runsim.run()

