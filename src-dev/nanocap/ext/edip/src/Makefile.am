lib_LTLIBRARIES = edip.la

libdir= ${abs_top_builddir}/lib
LD_FLAGS = -all-static
AM_FCFLAGS = -O3 -ffree-form -g -fopenmp -fno-underscoring -fno-second-underscore
edip_la_SOURCES = checkcell.f90\
					checkinput.f90\
					checkrij.f90\
					constants.f90\
					conductivity.f90\
					coordination.f90\
					cutoff.f90\
					defaults.f90\
					density.f90\
					dihedral.f90\
					dihedral2.f90\
					dihedral4.f90\
					distance.f90\
					distnab.f90\
					distribution.f90\
					edgetherm.f90\
					energy.f90\
					force.f90\
					init.f90\
					linear.f90\
					main.f90\
					makespecial.f90\
					neighbour.f90\
					pair.f90\
					parse.f90\
					printav.f90\
					printfinish.f90\
					printinput.f90\
					printrings.f90\
					printstatus.f90\
					printtime.f90\
					properties.f90\
					readcoords.f90\
					readinput.f90\
					remspace.f90\
					repulsion.f90\
					resetmsd.f90\
					stress.f90\
					therm.f90\
					triple.f90\
					volume.f90\
					verlet.f90\
					writecoords.f90\
					writegr.f90\
					writestress.f90\
					writetheta.f90\
					writexbs.f90\
					passcoords.f90\
					getforce.f90

edip_la_LDFLAGS = -module -avoid-version -O3 -ffree-form -g -fopenmp -fno-underscoring -fno-second-underscore  -shared

