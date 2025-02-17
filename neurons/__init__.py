# TODO(developer): Change this value when updating your code base.
# Define the version of the template module.


__version__ = "3.9.0"


version_split = __version__.split(".")
__spec_version__ = (
    (100000 * int(version_split[0]))
    + (10000 * int(version_split[1]))
    + (1000 * int(version_split[2]))
)


print(__spec_version__)