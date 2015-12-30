# Launch this with "python customsim.py 2 10"
# to get a network with 2 Mitral cells and 10 Granule cells/Mitral (20 total)

if __name__ == '__main__':

def main():
    import sys
    import custom_params
    custom_params.filename = 'fig7'

    offset = 0
    if len(sys.argv) >= 2 and sys.argv[1] == "-python":
        offset = 2

    if len(sys.argv) > 1:
        mitralArg = int(sys.argv[1+offset])
        granArg = int(sys.argv[2+offset])

        custom_params.customMitralCount = mitralArg
        custom_params.customGranulesPerMitralCount = granArg

    import params
    import runsim
    runsim.build_complete_model('c10.dic')
    runsim.run()

if __name__ == '__main__':
    main()