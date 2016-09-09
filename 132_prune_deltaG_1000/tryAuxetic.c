import io;
import python;
import location;
import string;
//string fileName = "/home/daniel/Documents/auxetic/runs/027_create_finite/starting_config_4_2_nParticles_300.xml";
//string fileName = "/home/daniel/Documents/auxetic/runs/027_create_finite/starting_config_5.000000_nParticles_2000_aspect_1.000000.xml";
string fileName = "/home/danielreid/swift-auxetic/runs/027_create_finite/finite_5.000000_nParticles_1000_sigma_2.000000_wallk_3.000000.xml";

string cutsDone[];
cutsDone[0] = "";
string importSim = """
import drivers
drivers.importSim()
""";


string countBonds = """
drivers.countBonds(\"%s\")
""" % fileName;

string setupInitState = """
drivers.setupInitState(\"%s\")
""" % fileName;

int nBondInit = string2int(python_persist(importSim, countBonds));

printf("num bonds %d", nBondInit);


string setupsDone[];

string loggedShearStresses[];

string loggedZs[];
string loggedBulkMods[];
string loggedShearMod1s[];
string loggedShearMod2s[];
string loggedPoissonsRatios[];

string gisFn = "\"Gis.dat\"";
string deltaGisFn = "\"deltaGis.dat\"";
string infoFn = "\"info.dat\"";
string cutBondsFn = "\"cutBonds.dat\"";

int nWorkers = turbine_workers();
foreach i in [0:nWorkers-1] {
    location L = rank2location(i);
    setupsDone[i] = @location = L python_persist("import drivers", setupInitState);
}

float targetZ = 3.5;

string fnsToClear[];
fnsToClear[0] = gisFn;
fnsToClear[1] = deltaGisFn;
fnsToClear[2] = infoFn;
fnsToClear[3] = cutBondsFn;
string fnsToClearJoin = join(fnsToClear, ",");

setupsDone[nWorkers] = python_persist("import drivers", "drivers.clearFiles([%s])" % fnsToClearJoin);
setupsDone[nWorkers+1] = python_persist("import drivers", "drivers.writeInfoHeader(%s, %s)" % (infoFn, setupsDone[nWorkers]));
loggedZs[-1] = float2string(targetZ + 1); //soooo we're always trimming at least one.  That's okay.  Or could play around with dependencies.
string setupsDoneAll = join(setupsDone, ",");

int nToTrim = 1500;

foreach nTrimmed in [0:nToTrim-1] {
    string stresses[];
    string writesFinished[];
    //add stuff to measure bulk, shear moduli as well as poisson's ratio
    loggedShearStresses[nTrimmed] = python_persist("import drivers", "drivers.measureStressNoCut(\"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    loggedZs[nTrimmed] = python_persist("import drivers", "drivers.measureZ(\"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    loggedBulkMods[nTrimmed] = python_persist("import drivers", "drivers.measureBulkMod(\"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    loggedShearMod1s[nTrimmed] = python_persist("import drivers", "drivers.measureShearMod(\"1\", \"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    loggedShearMod2s[nTrimmed] = python_persist("import drivers", "drivers.measureShearMod(\"2\", \"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    loggedPoissonsRatios[nTrimmed] = python_persist("import drivers", "drivers.measurePoissonsRatio(\"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed]));
    printf("Z current is %f", string2float(loggedZs[nTrimmed]));

	int numBonds = string2int(python_persist("import drivers", "drivers.countBendingBonds(\"%s\", [%s])" % (setupsDoneAll, cutsDone[nTrimmed])));
	printf("num bonds is %d", numBonds);
    foreach bondIdx in [0:numBonds-1] {//nBondInit-1-nTrimmed] {
        string script = "drivers.measureStress(%d, \"%s\", [%s])" % (bondIdx, setupsDoneAll, cutsDone[nTrimmed]); //basically mod, so they all get used
        stresses[bondIdx] = python_persist("import drivers", script);
    }
    string stressesJoin = join(stresses, ",");

    string execStr = "drivers.pickIdxToCut(\"\"\"[%s]\"\"\")" % stressesJoin;

    bondIdxToPrune = python_persist("import drivers", execStr);
	
    writesFinished[0] = python_persist("import drivers", "drivers.writeArray(%s, %s)" % (gisFn, loggedShearStresses[nTrimmed]));
    writesFinished[1] = python_persist("import drivers", "drivers.writeInfo(%s, [%s, %s, %s, %s, %s])" % (infoFn, loggedZs[nTrimmed], loggedBulkMods[nTrimmed], loggedShearMod1s[nTrimmed], loggedShearMod2s[nTrimmed], loggedPoissonsRatios[nTrimmed]));
    writesFinished[2] = python_persist("import drivers", "drivers.writeArray(%s, \"\"\"[%s]\"\"\")" % (deltaGisFn, stressesJoin));
	writesFinished[3] = python_persist("import drivers", "drivers.writeInfo(%s, [%s])" % (cutBondsFn, bondIdxToPrune));

    writesFinishedJoin = join(writesFinished, ",");

    string cuts[];
    foreach workerIdx in [0:nWorkers-1] {
        location L = rank2location(workerIdx);
        cuts[workerIdx] = @location = L python_persist("import drivers", "drivers.cutBond(%s, \"\"\"[%s]\"\"\")" % (bondIdxToPrune, writesFinishedJoin));
    }
    string cutsJoin = join(cuts, ",");


    cutsDone[nTrimmed+1] = cutsJoin;
}
