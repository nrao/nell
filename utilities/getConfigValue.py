import os


def getConfigValue(defaultValue, name, configFile): 
    """
    Cannabilised from sparrow, this reads values from a config file, 
    like /home/gbt/etc/config/system.conf.
    """
   
    # Get installation definition
    #ygorTelescope = os.environ["YGOR_TELESCOPE"]
    # Open the configuration file
    #if configFile[0] == '/':
    #    filename = configFile
    #else:
    #    filename = ygorTelescope + "/etc/config/" + configFile
    #config_file = open(filename, 'r')
    config_file = open(configFile, 'r')

    # Get the configuration values
    #keywords = { "YGOR_TELESCOPE" : ygorTelescope }
    keywords = {}
    for line in config_file.readlines():
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
           continue
        tokens = line.split(':=')
        if len(tokens) == 2:
            # Remove quotes
            parse = tokens[1].split('"')
            if len(parse) == 3:
                value = parse[1]
            else:
                value = tokens[1]
            keywords[tokens[0].strip()] = value.strip()
        else:
            print "Bad syntax in file %s: %s" % (filename, line)

    # Get the value from the environment, the file, or the default
    if os.environ.has_key(name):
        return os.environ[name]
    if keywords.has_key(name):
        return keywords[name]
    if defaultValue:
        return defaultValue
    raise KeyError, "No defined or default value for %s" % name

