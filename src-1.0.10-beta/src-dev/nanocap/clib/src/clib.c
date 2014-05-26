#include <time.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

//double pi;

int checkPlanarTriangles(double *ip0,double *jp0,double *kp0,
						 double *norm0,
						 double *ip,double *jp,double *kp);
int getIfIntersect(double* v0, double* v1,double* v2,double* d,double* origin);
int get_rings_of_vertex(int v0,
						int* Verts,
						int MaxVerts,
						int* NebList,
					    int* NebCount,
					    int MaxNebs,
					    int npoints,
					    int* removed,
					    int* Rings,
					    int* VertsPerRingCount,
					    int* nringsp);

int recursive_get_rings_of_vertex(int origin,
						int v0,
						int* Verts,
						int MaxVerts,
						int* NebList,
					    int* NebCount,
					    int MaxNebs,
					    int npoints,
					    int* visited_verts,
					    int ringlength,
					    int* nrings,
					    int* removed,
					    int* Rings,
					    int* VertsPerRingCount);

int check_SP_ring(int* Verts,int ringlength,int* NebCount,int* NebList,int MaxNebs);



inline int iabs(int x)
{
    return (x > 0) ? x : -x;
}

double derfc(double x)
{
	double out;
	out = -1.0 * (2.0/sqrt(M_PI))*exp(-(pow(x,2)));
	return out;
}

double magnitude_diff2(double* vec1, double* vec2)
{
	double r2;
	r2 = (vec1[0] - vec2[0] )*(vec1[0]  - vec2[0] )+(vec1[1]  - vec2[1])*(vec1[1] - vec2[1])+(vec1[2] - vec2[2])*(vec1[2] - vec2[2]);
	return r2;


}

double magnitude(double x,double y,double z)
{
	double r2;
	r2 = x*x + y*y + z*z;
	return sqrt(r2);


}

double magnitude_diff(double* vec1, double* vec2)
{
	double r2;
	r2 = (vec1[0] - vec2[0])*(vec1[0]  - vec2[0])+(vec1[1]  - vec2[1])*(vec1[1] - vec2[1])+(vec1[2] - vec2[2])*(vec1[2] - vec2[2]);
	return sqrt(r2);


}

double dot(double* vec1, double* vec2)
{
    int i;
    double scalar;
    scalar=0.0;
    for(i=0;i<3;i++)
    {
    scalar+=vec1[i]*vec2[i];
    }
    return scalar;
}

void cross(double* vec1, double* vec2,double* outvec)
{
	outvec[0] = (vec1[1]*vec2[2]) - (vec1[2]*vec2[1]);
	outvec[1] = (vec1[2]*vec2[0]) - (vec1[0]*vec2[2]);
	outvec[2] = (vec1[0]*vec2[1]) - (vec1[1]*vec2[0]);

	//printf(" vec1 %lf %lf %lf \n",vec1[0],vec1[1],vec1[2]);
	//printf(" vec2 %lf %lf %lf \n",vec2[0],vec2[1],vec2[2]);

	//printf(" outvec %lf %lf %lf \n",outvec[0],outvec[1],outvec[2]);
}

void get_unit_cell_xyz(int i, double theta_A, double rad,
					   double z_boundary,double theta_Ch_R,double magR,
					   int u,double magT,double boundary,
					   double angle, double offset, double* xyz)
{
		double id,kd;
		//double xyz[3];
		int k;
		id = (double) i;

		xyz[0] = rad * cos(id*theta_A + angle);
		xyz[1] = rad * sin(id*theta_A + angle);
        k = (int) (id*magR/z_boundary);
        kd = (double) k;
        xyz[2] = (id*magR  - kd*z_boundary) * sin(theta_Ch_R) - offset;

        xyz[2]+=(float) u * magT;
		if(xyz[2]<0){
			xyz[2]+=boundary;
		}
		if(xyz[2] > (boundary-1e-6)){
			xyz[2]-=boundary;
		}


        //return xyz;
}

void get_unit_cell_xyz_2D(int i, double theta_A, double rad,
						  double z_boundary,double theta_Ch_R,double magR,
						  double magCh,int u,double magT,double boundary,
						  double angle, double offset, double* xz)
{
	 	double id,kd;
		//double xz[3];
		int k;
		id = (double) i;

        xz[0] = id * (theta_A/(2.0*M_PI)) + angle/(2.0*M_PI);
        xz[0] *= magCh;
        k = (int) (id*magR/z_boundary);
		kd = (double) k;

        xz[1] = (id*magR  - kd*z_boundary) * sin(theta_Ch_R) - offset;
        xz[1]+= (float) u * magT;
		if(xz[1]< 0){
			xz[1]+=boundary;
		}
		if(xz[1] > (boundary-1e-6)){
			xz[1]-=boundary;
		}

        //return xz;
}

void build_nanotube(int ndual, double* dualLattice,
					int ncarbon, double* carbonLattice,
					int nintersect2D, double* intersection2D,

					int  Nhex,
					double units,
					double magT,
					double magR,
					double magCh,
					double rad,


					double theta_A,
					double theta_Ch_R,
					double z_boundary,

					double phi_A ,
					double phi_B ,
					double phi_D ,
					double phi_I1 ,
					double phi_I2 ,
					double phi_I3 ,

					double delta_A ,
					double delta_B ,
					double delta_D ,
					double delta_I1 ,
					double delta_I2 ,
					double delta_I3
					)
{
	double boundary;
	int atomcount,dualcount,intersectcount;
	int u,i;
	boundary = units*magT;
	atomcount = 0;
	dualcount = 0;
	intersectcount = 0;
	double xyz[3],xz[2];

	for (u = 0; u < units; u++)
	{
		for (i = 0; i < Nhex; i++)
		{
			//----A Atoms-----
			get_unit_cell_xyz(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,u,magT,boundary,
								   phi_A, delta_A,xyz);

			carbonLattice[atomcount*3] = xyz[0];
			carbonLattice[atomcount*3+1] = xyz[1];
			carbonLattice[atomcount*3+2] = xyz[2];
			atomcount++;

			//----B Atoms-----
			get_unit_cell_xyz(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,u,magT,boundary,
								   phi_B, delta_B,xyz);
			carbonLattice[atomcount*3] = xyz[0];
			carbonLattice[atomcount*3+1] = xyz[1];
			carbonLattice[atomcount*3+2] = xyz[2];
			atomcount++;

			//----Dual Lattice-----
			get_unit_cell_xyz(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,u,magT,boundary,
								   phi_D, delta_D,xyz);
			dualLattice[dualcount*3] = xyz[0];
			dualLattice[dualcount*3+1] = xyz[1];
			dualLattice[dualcount*3+2] = xyz[2];
			dualcount++;

			//----Intersection Points-----
			get_unit_cell_xyz_2D(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,magCh,u,magT,boundary,
								   phi_I1, delta_I1,xz);
			intersection2D[intersectcount*3] = xz[0];
			intersection2D[intersectcount*3+1] = 0;
			intersection2D[intersectcount*3+2] = xz[1];
			intersectcount++;

			get_unit_cell_xyz_2D(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,magCh,u,magT,boundary,
								   phi_I2, delta_I2,xz);
			intersection2D[intersectcount*3] = xz[0];
			intersection2D[intersectcount*3+1] = 0;
			intersection2D[intersectcount*3+2] = xz[1];
			intersectcount++;

			get_unit_cell_xyz_2D(i, theta_A, rad,
								   z_boundary,theta_Ch_R,magR,magCh,u,magT,boundary,
								   phi_I3, delta_I3,xz);

			intersection2D[intersectcount*3] = xz[0];
			intersection2D[intersectcount*3+1] = 0;
			intersection2D[intersectcount*3+2] = xz[1];
			intersectcount++;

		}

	}

}

void random_tangential_pertubation(int npoints,
								   double* pos,
								   double* freeflagspos,
								   double maxoffset,
								   int isNanotube)
{
	int i;
	double xo,yo,zo,magr,dp;

	double dr[3],r[3];


	for (i = 0; i < npoints; i++)
		    {
		    //printf(" --------- %d --------- \n",i);


		    xo =  (((double)rand()/(double)RAND_MAX) * 2.0)-1.0;
		    yo =  (((double)rand()/(double)RAND_MAX) * 2.0)-1.0;
		    zo =  (((double)rand()/(double)RAND_MAX) * 2.0)-1.0;

		    magr = magnitude(xo,yo,zo);

//		    printf("x0 %lf ", xo);
//			printf("y0 %lf ", yo);
//			printf("z0 %lf ", zo);
//			printf("magr %lf \n",magr);

		    dr[0] = xo/magr;
		    dr[1] = yo/magr;
		    dr[2] = zo/magr;

		    r[0] = pos[i*3];
		    r[1] = pos[i*3+1];
		    r[2] = pos[i*3+2];

//		    printf("rx %lf ", r[0] );
//			printf("ry %lf ", r[1] );
//			printf("rz %lf ", r[2] );
//			printf("magr %lf \n",magr);

		    dp = dot(dr,r);
//		    printf("dp %lf \n",dp);
//
//		    printf("x %lf ",(dr[0] - dp*r[0]) *maxoffset *freeflagspos[i*3]);
//		    printf("y %lf ",(dr[1] - dp*r[1]) *maxoffset *freeflagspos[i*3+1]);
//		    printf("z %lf \n",(dr[2] - dp*r[2]) *maxoffset *freeflagspos[i*3+2]);

		    pos[i*3] += (dr[0] - dp*r[0]) *maxoffset *freeflagspos[i*3] ;
		    pos[i*3+1] += (dr[1] - dp*r[1]) *maxoffset *freeflagspos[i*3+1];
		    pos[i*3+2] += (dr[2] - dp*r[2]) *maxoffset *freeflagspos[i*3+2];

		    }

}

int construct_neb_list(int npoints,
						int* NebList,
						int* NebCount,
						int MaxNebs,
						double cutoff,
						double* pos)
{
	double r2,cutoff2;
	int i,j;

	cutoff2 = cutoff*cutoff;

	//printf("in c construct nebs\n");
	for (i = 0; i < npoints; i++)
	    {
		for (j = i+1; j < npoints; j++)
			    {


					r2 = (pos[i*3]-pos[j*3])*(pos[i*3]-pos[j*3]);
					r2 += (pos[i*3+1]-pos[j*3+1])*(pos[i*3+1]-pos[j*3+1]);
					r2 += (pos[i*3+2]-pos[j*3+2])*(pos[i*3+2]-pos[j*3+2]);


					if(NebCount[i]+1>MaxNebs-1){
						printf("common.c Error too many neighbours\n");
						return -1;
					}
					if(NebCount[j]+1>MaxNebs-1){
						printf("common.c Error too many neighbours\n");
						return -1;
					}
					if(r2<cutoff2)
						{
						NebList[i*MaxNebs + NebCount[i]] = j;
						NebList[j*MaxNebs + NebCount[j]] = i;
						NebCount[i]++;
						NebCount[j]++;
						}

				}

	    }

	return 1;
}

void calc_volume_from_rings_using_div_thereom(int nrings,
											  int maxverts,
											  int* rings,
											  int* vertsPerRingCount,
											  double* pos,
											  double* out)
{
	/* Uses divergence theorem. Discrete volumes of each ring using normal.
	 *
	 *  /// div(F) dV = //  x.n dA
	 *
	 *  define F = (1,0,0), div(F) = 1
	 *
	 *  /// 1 dV = // x.n dA
	 *
	 *  V = sum (x*n*at) , at is area of polygon, x is center[0], n is normal[0] i.e. at (1,0,0)
	 *
	 * http://www.mathworks.com.au/matlabcentral/fileexchange/15221-triangulationvolume/content/triangulationVolume.m
	 *
	 * maybe check normals are outward facing...
	 */

	double area,vol,magc,ta,tv,dp;
	int i,j,k,jindex1,jindex0;
	int v1,v2,v3;

	double p1[3],p2[3],p3[3],totxyz[3],p[3],n[3],center[3];

	vol = 0.0;
	area = 0.0;
	for(i=0;i<nrings;i++){

		v1 = rings[i*maxverts];
		v2 = rings[i*maxverts + 1];
		v3 = rings[i*maxverts + 2];


		for(j=0;j<3;j++){
			p1[j] = pos[v3*3+j] - pos[v1*3+j];
			p2[j] = pos[v3*3+j] - pos[v2*3+j];
		}

		cross(p1,p2,p3);
		magc = magnitude(p3[0],p3[1],p3[2]);

		for(j=0;j<3;j++){
			n[j] = p3[j]/magc;
			totxyz[j] = 0.0;
			center[j] = 0.0;
		}

//		dp = dot(p1,n);
//		//printf(" dp %lf \n",dp);
//		if(dp<0){
//			cross(p2,p1,p3);
//			for(j=0;j<3;j++){
//				n[j] = p3[j]/magc;
//			}
//			//dp = dot(v1,n);
//			//printf(" corrected dp %lf \n",dp);
//		}




		for(j=0;j<vertsPerRingCount[i];j++){

			jindex0 = j;
			jindex1 = ((j+1) % vertsPerRingCount[i]);
			v1 = rings[i*maxverts + jindex0];
			v2 = rings[i*maxverts + jindex1];

			for(k=0;k<3;k++)
			{
				p1[k] = pos[v1*3+k];
				p2[k] = pos[v2*3+k];

			}

			cross(p1,p2,p3);
//			dp = dot(p3,n);
//			//printf(" dp %lf \n",dp);
//			if(dp<0){
//				cross(p2,p1,p3);
//				//for(j=0;j<3;j++){
//				//	n[j] = c[j]/magc;
//				//}
//				//dp = dot(v1,n);
//				//printf(" corrected dp %lf \n",dp);
//			}

			for(k=0;k<3;k++)
			{
				center[k] +=  pos[v1*3+k]/vertsPerRingCount[i];
				totxyz[k] += p3[k];
			}

		}

		/*As we do fabs, it does not matter that the normals are outward
		 *facing. Otherwise use v1.n to indicate if the sign of n is correct.
		 *As below check dp and reverse the cross product if < 0
		 */


		ta = fabs( dot(totxyz,n) / 2.0);
		tv = fabs( center[0] * n[0] * ta);



		vol = vol + tv;
		area = area + ta;

		//printf(" current volume %lf %lf %lf\n",vol,tv,center[0]);


	}
	//printf("triangulated surface area %lf \n",area);
	//printf("triangulated volume %lf \n",vol);
	out[0] = area;
	out[1] = vol;

}


void calc_volume_using_div_thereom(int ntri, int* verts, double* pos, double* out)
{
	/* Uses divergence theorem. Discrete volumes of each triangle using normal.
	 *
	 *  /// div(F) dV = //  x.n dA
	 *
	 *  define F = (1,0,0), div(F) = 1
	 *
	 *  /// 1 dV = // x.n dA
	 *
	 *  V = sum (x*n*at) , at is area of triangle
	 *
	 * http://www.mathworks.com.au/matlabcentral/fileexchange/15221-triangulationvolume/content/triangulationVolume.m
	 *
	 * maybe check normals are outward facing...
	 */

	double area,vol,magc,ta,tv,dp;
	int i,j,u,v,w;

	double a[3],b[3],c[3],nc[3],p[3],n[3],v1[3];

	vol = 0.0;
	area = 0.0;
	for(i=0;i<ntri;i++){

		u = verts[i*3];
		v = verts[i*3+1];
		w = verts[i*3+2];

		for(j=0;j<3;j++){
			a[j] = pos[v*3+j] - pos[u*3+j];
			b[j] = pos[w*3+j] - pos[u*3+j];
			v1[j] = pos[u*3+j];
		}

		cross(a,b,c);
		magc = magnitude(c[0],c[1],c[2]);
		ta = 0.5*magc;

		//printf(" area of triangle %d is %lf\n",i,ta);

		for(j=0;j<3;j++){
			p[j] = (pos[u*3+j] + pos[v*3+j] + pos[w*3+j])/3.0;
			n[j] = c[j]/magc;

			//printf(" n %lf ",n[j]);
		}

		/*As we do fabs, it does not matter that the normals are outward
		 *facing. Otherwise use v1.n to indicate if the sign of n is correct.
		 *As below check dp and reverse the cross product if < 0
		 */

		dp = dot(v1,n);
		//printf(" dp %lf \n",dp);
		if(dp<0){
			cross(b,a,c);
			for(j=0;j<3;j++){
				n[j] = c[j]/magc;
			}
			//dp = dot(v1,n);
			//printf(" corrected dp %lf \n",dp);
		}


		//tv = fabs(p[0] * n[0] * ta);
		tv = (p[0] * n[0] * ta);

		vol = vol + tv;
		area = area + ta;

		//printf(" current volume %lf \n",vol);


	}
	//printf("triangulated surface area %lf \n",area);
	//printf("triangulated volume %lf \n",vol);
	out[0] = area;
	out[1] = vol;

}

//typedef struct EdgeStruct Edge;
//
//typedef struct TriangleStruct Triangle;
//
//struct EdgeStruct{
//	//int  maxtri;
//	int  points[2];
//	int  ntriangles;
//	int  triangles[10];
//	//Triangle* triangles[2];
//};
//
//
//struct TriangleStruct{
//	int  points[3];
//	Edge* edges[3];
//};
//



int triangulate(int npoints,double* pos,int* culled_outtriangleindexs,
		 double* culled_outcenters,double* AvBondLength )
{

	int count;
	int MAXTRI;
	int i,j,k,d,m,found,dz,t;



	//char * test;
	//npoints = posdim/3;
    //printf(" in C , %d \n",npoints);
    //scanf("%s", &test);
    MAXTRI = npoints*5;
	double ij,jk,ik;

//	int nedges;
//	nedges = 0;
//	Edge* edges = malloc(3*MAXTRI*sizeof(Edge));
//
//	for (i = 0; i < 3*MAXTRI; i++)
//	{
//		edges[i].ntriangles=0;
//	}

	//Triangle* triangles = malloc(MAXTRI);

	//edges = (Edge*) malloc(nedges*sizeof(Edge));


//	double centers[MAXTRI*3];
//	double radius[MAXTRI];
//	double norms[MAXTRI*3];
//	int outtriangleindexs[MAXTRI*3];
//	double outcenters[MAXTRI*3];
//    int alltriangles[MAXTRI*3];

    int *alltriangles,*outtriangleindexs;
    alltriangles = (int*) malloc(3*MAXTRI*sizeof (int));
    outtriangleindexs = (int*) malloc(3*MAXTRI*sizeof (int));

    double *radius,*centers,*norms,*outcenters;
    radius = (double*) malloc(MAXTRI*sizeof (double));
    centers = (double*) malloc(3*MAXTRI*sizeof (double));
    norms = (double*) malloc(3*MAXTRI*sizeof (double));
    outcenters = (double*) malloc(3*MAXTRI*sizeof (double));


	double ip[3],jp[3],kp[3],mp[3],ccenter[3];
	double ip0[3],jp0[3],kp0[3];
	double ijv[3],ikv[3],jkv[3];
	double jiv[3],kiv[3],kjv[3];

	double alpha,beta,gamma,top,bottom,rad,disttocenter,magcross;
	double cp[3],nullv[3];
	double bondfactor=1.6;

	double zaxis[]= {0.0,0.0,1.0};


    //printf(" in C , %d \n",npoints);

	nullv[0] = 0.0;
	nullv[1] = 0.0;
	nullv[2] = 0.0;
	count = 0;

	int triangle_count=0;

	for (i = 0; i < npoints; i++)
	{
		ip[0] = pos[i*3];
		ip[1] = pos[i*3+1];
		ip[2] = pos[i*3+2];
		//printf(" point i, %d %lf %lf %lf \n",i,ip[0],ip[1],ip[2]);

		for (j = i+1; j < npoints; j++)
		{
			jp[0] = pos[j*3];
			jp[1] = pos[j*3+1];
			jp[2] = pos[j*3+2];
			//printf(" point j, %d %lf %lf %lf \n",j,jp[0],jp[1],jp[2]);
			ij = magnitude_diff(ip,jp);
			if(ij>AvBondLength[i]*bondfactor){
                   continue;
			}
			for (k = j+1; k < npoints; k++)
			{
				kp[0] = pos[k*3];
				kp[1] = pos[k*3+1];
				kp[2] = pos[k*3+2];
				//printf(" point k, %d %lf %lf %lf \n",k,kp[0],kp[1],kp[2]);
				ik = magnitude_diff(ip,kp);
				jk = magnitude_diff(jp,kp);
				//printf(" mag ik jk, %lf %lf \n",ik,jk);
				if(ik>AvBondLength[i]*bondfactor || jk>AvBondLength[i]*bondfactor){
                            	continue;
				}
				for (d = 0; d <3; d++){
				ijv[d] = ip[d] - jp[d];
				jiv[d] = jp[d] - ip[d];

				ikv[d] = ip[d] - kp[d];
				kiv[d] = kp[d] - ip[d];

				jkv[d] = jp[d] - kp[d];
				kjv[d] = kp[d] - jp[d];
				}
				//check collinear
				cross(ijv,jkv,cp);
				magcross = magnitude_diff(cp,nullv);
				cp[0]/=magcross;
				cp[1]/=magcross;
				cp[2]/=magcross;
				dz = dot(cp,zaxis);

				//printf("triangle norm %lf %lf %lf %lf\n",cp[0],cp[1],cp[2],dz);

				//printf("magcross %lf \n",magcross);
				if(magcross < 0.001){
					printf("points collinear magcross %lf\n",magcross);
					continue;}

				top = (ij * jk * ik);
				//printf("top %lf \n",top);
				bottom = 2.0*magcross;
				//printf("bottom %lf \n",bottom);
				rad = top/bottom;


				alpha =  (jk*jk)*dot(ijv,ikv);
				alpha /= 2.0*magcross*magcross;
				//printf("alpha %lf %lf %lf %lf\n",alpha,cp[0],cp[1],cp[2]);
				beta =  (ik*ik)*dot(jiv,jkv);
				beta /= 2.0*magcross*magcross;
				//printf("beta %lf \n",beta);
				gamma = (ij*ij)*dot(kiv,kjv);
		        gamma /= 2.0*magcross*magcross;
				//printf("gamma %lf \n",gamma);

		        //calculate circumcenter
		        ccenter[0] = alpha*ip[0] + beta*jp[0] + gamma*kp[0];
				ccenter[1] = alpha*ip[1] + beta*jp[1] + gamma*kp[1];
				ccenter[2] = alpha*ip[2] + beta*jp[2] + gamma*kp[2];



				found=0;
				for (m = 0; m < npoints; m++)
				{
						if(m==i || m==j || m==k){continue;}
						mp[0] = pos[m*3]-ccenter[0];
						mp[1] = pos[m*3+1]-ccenter[1];
						mp[2] = pos[m*3+2]-ccenter[2];
						disttocenter = magnitude_diff(mp,nullv);
						if(disttocenter<=rad){
							found = 1;
							break;
							  }

				}
				if(found==1){continue;}

				//the centers should be taken as the centroid
				ccenter[0] =  (ip[0] + jp[0] + kp[0])/3.0;
				ccenter[1] =  (ip[1] + jp[1] + kp[1])/3.0;
				ccenter[2] =  (ip[2] + jp[2] + kp[2])/3.0;

				radius[count] = rad;
				//printf("rad %lf count %d \n",rad,count);
				//printf(" centers %lf %lf %lf \n",ccenter[0],ccenter[1],ccenter[2]);
		        centers[count*3] = ccenter[0];
				centers[count*3+1] = ccenter[1];
				centers[count*3+2] = ccenter[2];

				//printf(" i,j,k %d %d %d \n",i,j,k);
//				printf(" ip %lf %lf %lf \n",ip[0],ip[1],ip[2]);
//				printf(" jp %lf %lf %lf \n",jp[0],jp[1],jp[2]);
//				printf(" kp %lf %lf %lf \n",kp[0],kp[1],kp[2]);

				//printf(" alpha %lf beta %lf gamma%lf magcp %lf %lf %lf %lf \n",alpha,beta,gamma,magnitude_diff(cp,nullv),cp[0],cp[1],cp[2]);
				//printf(" ijv %lf %lf %lf ",ijv[0],ijv[1],ijv[2]);
				//printf(" jkv %lf %lf %lf \n",jkv[0],jkv[1],jkv[2]);
				//printf(" v3 %lf %lf %lf \n",kp[0],kp[1],kp[2]);


				alltriangles[count*3] = i;
				alltriangles[count*3+1] = j;
				alltriangles[count*3+2] = k;

				outcenters[count*3] = ccenter[0];
				outcenters[count*3+1] = ccenter[1];
				outcenters[count*3+2] = ccenter[2];
				outtriangleindexs[count*3] = i;
				outtriangleindexs[count*3+1] = j;
				outtriangleindexs[count*3+2] = k;

				norms[count*3] = cp[0];
				norms[count*3+1] = cp[1];
				norms[count*3+2] = cp[2];

				if(count >=MAXTRI){
						printf("MAXTRI limit count %d npoints %d \n",count,npoints);
				}
				count+=1;
			}


		}

	}



	//Now we check for triangles constructed inside the close surface
	//Can happen if the diameter of the sphere/cylinder is of the same size as the
	//spacing between points

	triangle_count = count;

    //printf("**BEFORE REMOVAL %d \n",count)   ;

    //double orgin[] ={0,0,-10.0};
    double n[3],o[3];
    int t0,intersectf,intersectb,i0,j0,k0;
    int intersectf_count,intersectb_count;
    int planar;

    count = 0;
    for (t0 = 0; t0 < triangle_count; t0++)
	{
    	intersectf_count=0;
    	intersectb_count=0;

		o[0] = outcenters[t0*3];
		o[1] = outcenters[t0*3+1];
		o[2] = outcenters[t0*3+2];
		i0 = outtriangleindexs[t0*3];
		j0 = outtriangleindexs[t0*3+1];
		k0 = outtriangleindexs[t0*3+2];
		ip0[0] = pos[i0*3];
		ip0[1] = pos[i0*3+1];
		ip0[2] = pos[i0*3+2];

		jp0[0] = pos[j0*3];
		jp0[1] = pos[j0*3+1];
		jp0[2] = pos[j0*3+2];

		kp0[0] = pos[k0*3];
		kp0[1] = pos[k0*3+1];
		kp0[2] = pos[k0*3+2];

		//printf("index %d %d %d \n", i0,j0,k0);
		//printf("center %lf %lf %lf \n", o[0],o[1],o[2]);

		for (t = 0; t < triangle_count; t++)
		{
			//count intersections
			if(t0==t){continue;}


			i = outtriangleindexs[t*3];
			j = outtriangleindexs[t*3+1];
			k = outtriangleindexs[t*3+2];
			ip[0] = pos[i*3];
			ip[1] = pos[i*3+1];
			ip[2] = pos[i*3+2];

			jp[0] = pos[j*3];
			jp[1] = pos[j*3+1];
			jp[2] = pos[j*3+2];

			kp[0] = pos[k*3];
			kp[1] = pos[k*3+1];
			kp[2] = pos[k*3+2];

	    	n[0] = norms[t0*3];
			n[1] = norms[t0*3+1];
			n[2] = norms[t0*3+2];

			planar = checkPlanarTriangles(ip,jp,kp,n,ip0,jp0,kp0);

			if(planar==1){
				//printf("coplanar triangles %d %d %d and %d %d %d\n",i,j,k,i0,j0,k0);
				continue;}

			//interesction of ray n from origin o with plane ip,jp,kp

			intersectf  = getIfIntersect(ip,jp,kp,n,o);

			//printf("tri %d tri2 %d intersect %d\n",t0,t,intersect);

			if(intersectf==1){
				//printf("intersectf triangles %d %d %d and %d %d %d normal %lf %lf %lf\n",i,j,k,i0,j0,k0,n[0],n[1],n[2]);
				intersectf_count++;
			}

	    	n[0] = -1.0*norms[t0*3];
			n[1] = -1.0*norms[t0*3+1];
			n[2] = -1.0*norms[t0*3+2];



			intersectb  = getIfIntersect(ip,jp,kp,n,o);

			//printf("tri %d tri2 %d intersect %d\n",t0,t,intersect);

			if(intersectb==1){
				//printf("intersectb triangles %d %d %d and %d %d %d normal %lf %lf %lf \n",i,j,k,i0,j0,k0,n[0],n[1],n[2]);
				intersectb_count++;
			}
			if(intersectb_count>0 && intersectf_count>0){
				break;
			}


		}
		if(intersectb_count>0 && intersectf_count>0){
			// if a triangle's +ve and -ve normals intersect other triangles then this is an
			// enclosed triangle and should be culled.

			//printf("tri %d intersectf_count %d\n",t0,intersectf_count);
			//printf("tri %d intersectb_count %d\n",t0,intersectb_count);



			}
		else{
		//}
			culled_outcenters[count*3] = o[0];
			culled_outcenters[count*3+1] = o[1];
			culled_outcenters[count*3+2] = o[2];
			culled_outtriangleindexs[count*3] = i0;
			culled_outtriangleindexs[count*3+1] = j0;
			culled_outtriangleindexs[count*3+2] = k0;

			//printf("center %lf %lf %lf \n", culled_outcenters[count*3],culled_outcenters[count*3+1],culled_outcenters[count*3+2]);
			//printf("index %d %d %d \n", culled_outtriangleindexs[count*3],culled_outtriangleindexs[count*3+1],culled_outtriangleindexs[count*3+2]);


//			edges[nedges].points[0] = i0;
//			edges[nedges].points[1] = j0;
//			edges[nedges].triangles[0] = count;
//			//edges[nedges].ntriangles++;
//
//			nedges++;
//			edges[nedges].points[0] = j0;
//			edges[nedges].points[1] = k0;
//			edges[nedges].triangles[0] = count;
//			//edges[nedges].ntriangles++;
//			nedges++;
//			edges[nedges].points[0] = k0;
//			edges[nedges].points[1] = i0;
//			edges[nedges].triangles[0] = count;
//			//edges[nedges].ntriangles++;
//			nedges++;

			count++;
			//printf( "edge %d %d \n",edges[nedges-1].points[0],edges[nedges-1].points[1]);

		}
	}

    printf( "end \n");
    triangle_count = count;

//    //collate edges
//    int unique_nedges;
//    int t2;
//    unique_nedges = 0;
//    Edge* unique_edges = malloc(2*MAXTRI*sizeof(Edge));
//
//    for (i = 0; i < 2*MAXTRI; i++)
//    {
//    	unique_edges[i].ntriangles=0;
//    }
//
//    for (t = 0; t < nedges; t++)
//    {
//    	found = 0;
//    	for (t2 = 0; t2 < unique_nedges; t2++)
//    	    {
//
//    		found = compare_edges(unique_edges[t2],edges[t]);
//    		if(found==1){break;}
//    	    }
//
//    	if(found==0){
//    		unique_edges[unique_nedges].points[0] = edges[t].points[0];
//    		unique_edges[unique_nedges].points[1] = edges[t].points[1];
//    		unique_edges[unique_nedges].triangles[0] = edges[t].triangles[0];
//    		unique_edges[unique_nedges].ntriangles++;
//    		unique_nedges++;
//    	}
//    	else{
//    		unique_edges[t2].triangles[unique_edges[t2].ntriangles] = edges[t].triangles[0];
//    		unique_edges[t2].ntriangles++;
//
//    	}
//
//    }
//
//
//    printf("unique_nedges %d \n",unique_nedges);
////
////
////
////
////
//    int maxcull = unique_nedges*3/2;
//
//    int trilist[maxcull];
//    int c;
////	for (c = 0; c < maxcull; c++)
////	    {
////		culllist[c] = -1;
////	    }
//
//    count = 0;
//    for (t = 0; t < unique_nedges; t++)
//    {
//    	if(unique_edges[t].ntriangles > 2)
//    	{
//    		printf("edge %d (%d %d) has %d triangles\n", t,unique_edges[t].points[0],unique_edges[t].points[1],unique_edges[t].ntriangles );
//    		for (t2 = 0; t2 < unique_edges[t].ntriangles; t2++)
//    		  {
//
////    			for (c = 0; c < count; c++)
////    			    {
////    				if(culllist[c] == unique_edges[t].triangles[t2])
////    				{
//    			trilist[count] = unique_edges[t].triangles[t2];
//				count++;
////    					break;
////    				}
////
////    			    }
//
//    			printf("triangle %d \n",unique_edges[t].triangles[t2]);
//
//    		  }
//    	}
//    }
//    /*
//     * Here we remove triangles that share edges that themselves have
//     * > 2 triangles attached.
//     *
//     */
//    int culllist[maxcull];
//    int unilist[maxcull];
//    int ncull = 0;
//    int nunique = 0;
//    int nu;
//    int duplicate = 0;
//    for (c = 0; c < count; c++)
//    {
//    	for (nu = 0; nu < nunique; nu++)
//    	    {
//    			if(trilist[c] == unilist[nu])
//    			{
//    			duplicate = 1;
//    			break;
//    			}
//    	    }
//    	if(!duplicate) { // if our value wasn't found in 'b' we will add this non-dublicate at index
//    	   unilist[nunique] = trilist[c];
//    	   nunique++;
//		}
//    	else
//    	{
//    		culllist[ncull] = trilist[c];
//    		printf("triangle to cull due to shared edges %d\n",culllist[ncull]);
//    		ncull++;
//
//
//    	}
//    	duplicate = 0;
//
//    }

//    count = 0;
//    found = 0;
//    for (t = 0; t < triangle_count; t++)
//    {
//    	found=0;
//    	for (c = 0; c < ncull; c++)
//    	    {
//    		if(culllist[c]==t)
//    		{
//    			found=1;
//    			break;
//    		}
//
//    	    }
//    	if(found==0){
//    		culled_outcenters[count*3] = culled_outcenters[t*3];;
//			culled_outcenters[count*3+1] = culled_outcenters[t*3+1];
//			culled_outcenters[count*3+2] = culled_outcenters[t*3+2] ;
//			culled_outtriangleindexs[count*3] = culled_outtriangleindexs[t*3];
//			culled_outtriangleindexs[count*3+1] = culled_outtriangleindexs[t*3+1];
//			culled_outtriangleindexs[count*3+2] = culled_outtriangleindexs[t*3+2];
//			count++;
//    	}
//
//    }
//    triangle_count = count;



    //calc_volume_using_div_thereom(triangle_count,culled_outtriangleindexs,pos);
    //edges = NULL;
    //free(edges);
    //free(triangles);

	free(centers);
	free(radius);
	free(norms);
	free(outtriangleindexs);
	free(outcenters);
	free(alltriangles);

	//printf("triangle_count %d \n",triangle_count);

	return triangle_count;

}

//int compare_edges(Edge e1, Edge e2)
//{
//	int same = 0;
//	if(e1.points[0] == e2.points[0])
//	{
//		if(e1.points[1] == e2.points[1])
//		{
//			same=1;
//		}
//	}
//	if(e1.points[0] == e2.points[1])
//	{
//		if(e1.points[1] == e2.points[0])
//		{
//			same=1;
//		}
//	}
//	return same;
//}

void sep_vector(double* v1, double* v2, double* outv)
{
	outv[0] = v2[0]-v1[0];
	outv[1] = v2[1]-v1[1];
	outv[2] = v2[2]-v1[2];
}


int checkPlanarTriangles(double *ip0,double *jp0,double *kp0,
						 double *norm0,
						 double *ip,double *jp,double *kp)
{
	double xdiff,ydiff,zdiff,dotProd0,dotProd1,dotProd2;

	xdiff = ip0[0] - ip[0];
	ydiff = ip0[1] - ip[1];
	zdiff = ip0[2] - ip[2];

	dotProd0 = (xdiff*norm0[0])+(ydiff*norm0[1])+(zdiff*norm0[2]);
	xdiff = jp0[0] - jp[0];
	ydiff = jp0[1] - jp[1];
	zdiff = jp0[2] - jp[2];

	dotProd1 = (xdiff*norm0[0])+(ydiff*norm0[1])+(zdiff*norm0[2]);

	xdiff = kp0[0] - kp[0];
	ydiff = kp0[1] - kp[1];
	zdiff = kp0[2] - kp[2];

	dotProd2 = (xdiff*norm0[0])+(ydiff*norm0[1])+(zdiff*norm0[2]);

	if(abs(dotProd0)< 1e-5 && abs(dotProd1)< 1e-5 && abs(dotProd2)< 1e-5)
	{

		return 1;
	}
	else{
		return 0;
	}
}


int getIfIntersect(double* v0, double* v1,double* v2,double* d,double* origin)
{
	double e1[3],e2[3],pvec[3],tvec[3],qvec[3],ivec[3];
	double invDet,det,u,v,t;

	sep_vector(v0,v1,e1);
	sep_vector(v0,v2,e2);

    cross(d,e2,pvec);

    det = dot(e1,pvec);

//    if (det < 1e-5){
//            return 0;
//    }

    if (det > -0.00005 && det < 0.00005){
    	return 0;
    }

    invDet = 1.0 / det;

    sep_vector(v0,origin,tvec);

    u = dot(tvec, pvec) * invDet;

    if (u < 0.0 || u > 1.0){
        return 0;
    }

    cross(tvec, e1,qvec);

    v = dot(d, qvec) * invDet;

    if (v < 0.0 || u + v > 1.0){

        return 0;
	}

    t = dot(e2, qvec) * invDet;
    if(t>1e-5){
		ivec[0] = t*d[0] + origin[0];
		ivec[1] = t*d[1] + origin[1];
		ivec[2] = t*d[2] + origin[2];

		//printf("intersection point %lf %lf %lf\n",ivec[0],ivec[1],ivec[2]);

		return 1;
    }
	else{
		return 0;
	}
    //t = numpy.dot(e2, qvec) * invDet;
    //return 1,t*d + origin
}

void get_average_bond_length_diff(int npoints,double* pos,int npoints2,double* pos2,double* AvBondLength)
{
	int i,j;
	double rmin1,rmin2,rmin3,rmin4,rmin5,ij;
	double xdiff,ydiff,zdiff;
        for(i=0;i<npoints;i++){
            rmin1 = 1000;
            rmin2 = 1001;
            rmin3 = 1002;
            rmin4 = 1003;
            rmin5 = 1004;

            for(j=0;j<npoints2;j++){

		xdiff= pos[i*3]-pos2[j*3];
		ydiff= pos[i*3+1]-pos2[j*3+1];
		zdiff= pos[i*3+2]-pos2[j*3+2];
                ij = sqrt(xdiff*xdiff + ydiff*ydiff + zdiff*zdiff);

                if(ij<=rmin1){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = rmin2;
                    rmin2 = rmin1;
                    rmin1 =ij;
		}
                else if(ij>rmin1 && ij<=rmin2){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = rmin2;
                    rmin2 = ij;
		}
                else if(ij>rmin2 && ij<=rmin3){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = ij;
		}
                else if(ij>rmin3 && ij<=rmin4){
                    rmin5 = rmin4;
                    rmin4 = ij;
		}
                else if(ij>rmin4 && ij<=rmin5){
                    rmin5 = ij;
               }

	    }

            AvBondLength[i] = (rmin5+rmin4+rmin3+rmin2+rmin1)/5.0;
//AvBondLength[i] = rmin5;
	}
}


void get_average_bond_length_three(int npoints,double* pos,double* AvBondLength)
{
	int i,j;
	double rmin1,rmin2,rmin3,ij;
	double xdiff,ydiff,zdiff;
        for(i=0;i<npoints;i++){
            rmin1 = 1000;
            rmin2 = 1001;
            rmin3 = 1002;

            for(j=0;j<npoints;j++){
                if(i==j){continue;}

				xdiff= pos[i*3]-pos[j*3];
				ydiff= pos[i*3+1]-pos[j*3+1];
				zdiff= pos[i*3+2]-pos[j*3+2];
						ij = sqrt(xdiff*xdiff + ydiff*ydiff + zdiff*zdiff);
						if(ij<=rmin1){
							rmin3 = rmin2;
							rmin2 = rmin1;
							rmin1 =ij;
				}
						else if(ij>rmin1 && ij<=rmin2){

							rmin3 = rmin2;
							rmin2 = ij;
				}
						else if(ij>rmin2 && ij<=rmin3){
							rmin3 = ij;
				}
				  //printf("i %d, j, %d, %lf, %lf, %lf, %lf \n",i,j,ij,rmin1,rmin2,rmin3);

				}

            AvBondLength[i] = rmin3;
            //AvBondLength[i] = (rmin1 + rmin2 + rmin3 )/3.0;

	}
}

void get_bond_lengths_three(int npoints,double* pos,double* BondLengths)
{
	int i,j,count,set;
	double rmin1,rmin2,rmin3,ij;
	double xdiff,ydiff,zdiff;
	count= 0 ;

    for(i=0;i<npoints;i++){
            rmin1 = 1000;
            rmin2 = 1001;
            rmin3 = 1002;
            set = 0;
            for(j=0;j<npoints;j++){
                if(i==j){continue;}

				xdiff= pos[i*3]-pos[j*3];
				ydiff= pos[i*3+1]-pos[j*3+1];
				zdiff= pos[i*3+2]-pos[j*3+2];
				ij = sqrt(xdiff*xdiff + ydiff*ydiff + zdiff*zdiff);
				if(ij<=rmin1){
					rmin3 = rmin2;
					rmin2 = rmin1;
					rmin1 =ij;
					set = 1;
				}
				else if(ij>rmin1 && ij<=rmin2){

					rmin3 = rmin2;
					rmin2 = ij;
				}
				else if(ij>rmin2 && ij<=rmin3){
					rmin3 = ij;
				}
				  //printf("i %d, j, %d, %lf, %lf, %lf, %lf \n",i,j,ij,rmin1,rmin2,rmin3);

				}
            //if(set==1){
				BondLengths[count] = rmin1;
	            BondLengths[count+1] = rmin2;
	            BondLengths[count+2] = rmin3;
				count+=3;

				//printf("i %d, %d, %lf, %lf, %lf \n",i,count,rmin1,rmin2,rmin3);
            //}
            //AvBondLength[i] = (rmin1 + rmin2 + rmin3 )/3.0;

	}
}



int calculate_rings(int npoints,
				   int nedges,
				   int* NebList,
				   int* NebCount,
				   int MaxNebs,
				   int* Rings,
				   int* VertsPerRingCount,
				   int* RingsPerVertCount,
				   int MaxVerts,
				   double* pos)
{
	int i,nrings,temp;
	int *nringsp;
	int Verts[MaxVerts];


	int removed[npoints];
	for (i = 0; i < npoints; i++)
		{
		removed[i] =0;
		}

	nrings  = 0;
	nringsp = &nrings;
	//Visible = 3;
	for (i = 0; i < npoints; i++)
	{
		if(removed[i] ==1){continue;}

		//printf("getting rings of  %d \n",i);
		//find all rings of i up to MaxVerts
		temp = get_rings_of_vertex(i,Verts,MaxVerts,NebList,NebCount,MaxNebs,npoints,removed,
									Rings,VertsPerRingCount,nringsp);
		//nrings+=nringspervert;
		//printf("total rings of %d %d \n",i,*nringsp);
		removed[i] = 1;


	}
	//for each visible
	//for each ring
	return nrings;
}


int get_rings_of_vertex(int v0,
						int* Verts,
						int MaxVerts,
						int* NebList,
					    int* NebCount,
					    int MaxNebs,
					    int npoints,
					    int* removed,
					    int* Rings,
					    int* VertsPerRingCount,
					    int* nringsp)
{
	int neb,i,ringlength,temp;

	int visited_verts[npoints];

	for (i = 0; i < npoints; i++)
	{
		visited_verts[i] =0;
	}

	for (i = 0; i < NebCount[v0]; i++)
		{
			neb = NebList[v0*MaxNebs+i];

			if(removed[neb]==1){continue;}

			//printf("finding from vertex %d to neb  %d nebcount %d  \n",v0,neb,NebCount[v0]);
			ringlength = 2;
			Verts[0] = v0;
			Verts[1] = neb;
			temp = recursive_get_rings_of_vertex(v0,
									 neb,
									 Verts,
									 MaxVerts,
									 NebList,
									 NebCount,
									 MaxNebs,
									 npoints,
									 visited_verts,
									 ringlength,
									 nringsp,
									 removed,
									 Rings,
									 VertsPerRingCount);
			visited_verts[neb]=1;
		}

	return *nringsp;

}

int recursive_get_rings_of_vertex(int origin,
						int v0,
						int* Verts,
						int MaxVerts,
						int* NebList,
					    int* NebCount,
					    int MaxNebs,
					    int npoints,
					    int* visited_verts,
					    int ringlength,
					    int* nrings,
					    int* removed,
					    int* Rings,
					    int* VertsPerRingCount)
{
	int i,j,neb,dup,isSP,ringnumber;

	//visited_verts[v0]=1;

	for (i = 0; i < NebCount[v0]; i++)
		{
			neb = NebList[v0*MaxNebs+i];

			//printf("v0 %d checking neb %d\n",v0,neb);

			if(removed[neb]==1){continue;}
			if(visited_verts[neb]==1){continue;}

			dup=0;
			for (j = 0; j < ringlength; j++)
				{
				if(neb == Verts[j])
					{
						dup=1;
						break;
					}
				}

			if(dup==1){

				if(neb==origin && ringlength>2)
				{

					isSP = check_SP_ring(Verts,ringlength,NebCount,NebList,MaxNebs);
					if (isSP==1)
					{
						//printf("SP RING nrings for vertex %d\n",*nrings);
						ringnumber = *nrings;
						for (j = 0; j < ringlength; j++)
						{
							//printf(" %d ",Verts[j]);
							Rings[ringnumber*MaxVerts + j]  = Verts[j];
						}

						VertsPerRingCount[ringnumber] = ringlength;

						*nrings=*nrings+1;

					}

				}
				//already in path continue;
				continue;
			}
			//if not in path and path length is less that max, add and call recursively
			if(ringlength<MaxVerts){
				Verts[ringlength] = neb;
				ringlength++;

				ringlength = recursive_get_rings_of_vertex(origin,
											neb,
											Verts,
											MaxVerts,
											NebList,
											NebCount,
											MaxNebs,
											npoints,
											visited_verts,
											ringlength,
											nrings,
											removed,
											Rings,
											VertsPerRingCount);
			}
		}

	if(v0==Verts[ringlength-1]){ringlength--;}
	return ringlength;
}

void get_path_recursive(int previous,int from ,int target, int* currentLength,int* shortestLength,int* NebCount,int* NebList,int MaxNebs,int maxLength)
{
	int neb,i;

	*currentLength = *currentLength+1;
	for (i = 0; i < NebCount[from]; i++)
	{
		neb = NebList[from*MaxNebs+i];
		if(neb==previous){continue;}
		//if(target==11){printf("Testing From %d Neb %d length %d\n",from,neb,*currentLength);}
		if(neb!=target)
		{
			if(*currentLength<=maxLength)
			{
				get_path_recursive(from,neb,target,currentLength,shortestLength,NebCount,NebList,MaxNebs,maxLength);
			}
		}
		else
		{
			if(*currentLength<*shortestLength)
			{
				*shortestLength = *currentLength;
			}
			//printf("From %d Found target %d length %d\n",from,target,*currentLength);
		}
	}
	*currentLength = *currentLength-1;
	return;

}

int get_path_length(int v0,int v1,int* NebCount,int* NebList,int MaxNebs, int maxLength)
{
	int length;
	int currentLength,shortestLength;
	int* p;
	int* s;
	length = 0;

	currentLength = 0;
	p = &currentLength;

	shortestLength = 1000;
	s = &shortestLength;

	//printf("start currentLength %d \n",*p);
	get_path_recursive(-1,v0,v1,p,s,NebCount,NebList,MaxNebs,maxLength);
	//printf("From %d Found target %d shortestLength %d\n",v0,v1,shortestLength);
	return shortestLength;

}

int get_vert_dist(int v0,int v1,int* Verts,int ringlength)
{
	int i,p1,p2,d1,d2;
	p1=-1;
	p2=-1;
	for (i = 0; i < ringlength; i++)
	{
		if(Verts[i]==v0){p1=i;}
		else if(Verts[i]==v1){p2=i;}

		if(p1>-1 && p2>-1)
		{
			break;
		}
	}
	d1 = iabs(p2-p1);
	d2 = ringlength-d1;

	return (d1 < d2) ? d1 : d2;
}

int check_SP_ring(int* Verts,int ringlength,int* NebCount,int* NebList,int MaxNebs)
{

	int i,j,dR,dG;

	for (i = 0; i < ringlength; i++)
			{
		for (j = i+1; j < ringlength; j++)
					{

					dR = get_vert_dist(Verts[i],Verts[j],Verts,ringlength);
					//printf("getting path length v0 %d v1 %d maxlength %d\n",Verts[i],Verts[j],dR);
					dG = get_path_length(Verts[i],Verts[j],NebCount,NebList,MaxNebs,dR);
					//printf("v0 %d v1 %d dist %d %d\n",Verts[i],Verts[j],dR,dG);
					if(dR!=dG){
						return 0;
					}
					}
			}
	return 1;
}










void get_average_bond_length(int npoints,double* pos,double* AvBondLength)
{
	int i,j;
	double rmin1,rmin2,rmin3,rmin4,rmin5,ij;
	double xdiff,ydiff,zdiff;
        for(i=0;i<npoints;i++){
            rmin1 = 1000;
            rmin2 = 1001;
            rmin3 = 1002;
            rmin4 = 1003;
            rmin5 = 1004;

            for(j=0;j<npoints;j++){
                if(i==j){continue;}

		xdiff= pos[i*3]-pos[j*3];
		ydiff= pos[i*3+1]-pos[j*3+1];
		zdiff= pos[i*3+2]-pos[j*3+2];
                ij = sqrt(xdiff*xdiff + ydiff*ydiff + zdiff*zdiff);

                if(ij<=rmin1){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = rmin2;
                    rmin2 = rmin1;
                    rmin1 =ij;
		}
                else if(ij>rmin1 && ij<=rmin2){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = rmin2;
                    rmin2 = ij;
		}
                else if(ij>rmin2 && ij<=rmin3){
                    rmin5 = rmin4;
                    rmin4 = rmin3;
                    rmin3 = ij;
		}
                else if(ij>rmin3 && ij<=rmin4){
                    rmin5 = rmin4;
                    rmin4 = ij;
		}
                else if(ij>rmin4 && ij<=rmin5){
                    rmin5 = ij;
               }

	    }

            AvBondLength[i] = (rmin5+rmin4+rmin3+rmin2+rmin1)/5.0;
	}
}

int setup_nanotube_dualgraph(int npoints,double* pos, double* bondlength, int outnpoints, double* outpos)
{
	int i,j,k,found;
	double dx,dy,dz,r,x,y,z;
	double mag;
	//double temppos[outnpoints*3];
	int NTp = 0;

	for(i=0;i<npoints;i++)
	{

		for(j=i+1;j<npoints;j++)
		{
			dx = (pos[i*3] - pos[j*3]);
			dy = (pos[i*3+1] - pos[j*3+1]);
			dz = (pos[i*3+2] - pos[j*3+2]);
			r = sqrt(dx*dx + dy*dy + dz*dz);
			//printf("i %d j %d r %lf b1 %lf b2 %lf \n",i,j,r,bondlength[0],bondlength[1]);
			if(r>bondlength[0] && r<bondlength[1])
			{
				//printf("r %lf b1 %lf b2 %lf \n",r,bondlength[0],bondlength[1]);
				x = pos[i*3]  - (dx/2.0);
				y = pos[i*3+1]  - (dy/2.0);
				z = pos[i*3+2]  - (dz/2.0);
				mag = sqrt(x*x + y*y);
				x = x/mag;
				y = y/mag;
				//printf("C %d %lf %lf %lf   \n",i, x,y,z);
				//check for cooincidence.
				found=0;
				for(k=0;k<NTp;k++)
				{
					if(fabs(x-outpos[k*3])<0.01)
					{
						if(fabs(y-outpos[k*3+1])<0.01)
						{
							if(fabs(z-outpos[k*3+2])<0.01)
							{
								found=1;
								break;
							}
						}
					}
				}
				if(found == 0)
				{
					outpos[NTp*3] = x;
					outpos[NTp*3+1] = y;
					outpos[NTp*3+2] = z;
					NTp++;
					//printf("adding %d %lf %lf %lf \n",NTp, x,y,z);
				}
			}
		}
	}
	return NTp;

}

double get_mapping_angle(int npoints,double* pos,int npoints2,double* pos2,double* com,double deltaTheta)
{
	int found,i,j,foundcount,points,foundme;

	double pi,iter,x,y,z,xdiff,ydiff,zdiff,rsq,ci,si;
	pi = 4.0*atan(1.0);
	iter = deltaTheta;
    found = 0;
	foundcount = 0;

	double mappingAngle=0;
	points = npoints/2;
	points = npoints;
	printf(" pi %lf cospi %lf \n",pi,cos(pi));
    while(found==0 && iter<2*pi)
	{
        foundcount = 0;
        si =  sin(iter);
        ci =  cos(iter);
        //rmin = 1000000.0
        for(i=0;i<points;i++)
   		{
        	foundme = 0;
			x = pos[i*3]*ci - pos[i*3+1]*si;
			y = pos[i*3]*si + pos[i*3+1]*ci;
			z = pos[i*3+2];
			for(j=0;j<npoints;j++)
   			{
				xdiff= (x+com[0])-pos2[j*3];
				ydiff= (y+com[1])-pos2[j*3+1];
				zdiff= (z+com[2])-pos2[j*3+2];

				rsq = xdiff*xdiff + ydiff*ydiff + zdiff*zdiff;
			    //printf("iter %lf rsq %lf \n",iter,rsq);
				if(rsq<1e-5){
					foundcount+=1;
					foundme =1 ;
					break;
				}

			}
			if(foundme==0){
				break;
			}
		}
        //printf("iter %lf foundcount %d \n",iter,foundcount);
		if(foundcount==points){
			printf("iter %lf foundcount %d \n",iter,foundcount);
			mappingAngle = iter;
			found=1 ;
	    }

    iter+=deltaTheta;
	}
    if(found==0)
    {
    	printf("warning in C - did not find mapping angle\n");
    	mappingAngle = -1.0;
    }

    return mappingAngle;
}

void do_damp_force(double k,int npoints,double* force,double* pos,double* pos0,
				   double* energy,double* vel,int* dampflags)
{
	int i;
	double dx,dy,dz,r2,r,e,magf;
	for(i=0;i<npoints;i++)
	    {
		if(dampflags[i]==0){continue;}
		dx=pos[i*3]-pos0[i*3];
		dy=pos[i*3+1]-pos0[i*3+1];
		dz=pos[i*3+2]-pos0[i*3+2];
		r2 = dx*dx + dy*dy + dz*dz;
		r = sqrt(r2);
		if(r==0.0){continue;}
		magf = -1.0*k*r;
		e = (0.5*k*r2);
		energy[i] += e/2.0;
		//energy[j] += e/2.0;
		force[i*3] += magf*(dx/r);
		force[i*3+1] += magf*(dy/r);
		force[i*3+2] += magf*(dz/r);
//		force[j*3] -= magf*(dx/r);
//		force[j*3+1] -= magf*(dy/r);
//		force[j*3+2] -= magf*(dz/r);
		//printf("spring force %lf %lf %lf, %lf %lf %lf energy %lf \n",force[i*3],force[i*3+1],force[i*3+2],
		//		force[j*3],force[j*3+1],force[j*3+2],energy[i]);
	    }
}

double get_numerical(double r,double x1,double x2,double h)
{
	double fr,br,fenergy,benergy,u,arga,arge;
	double expo;
	expo=1.0;
	fr = r+h;
	u = (fr - x1)/(x2 - x1) * M_PI;
	arga = 1.0/(pow(fr,expo));
	arge = cos(u)/2.0 + 0.5;
	fenergy = arga*arge;

	br= r-h;
	u = (br - x1)/(x2 - x1) * M_PI;
	arga = 1.0/(pow(br,expo));
	arge = cos(u)/2.0 + 0.5;
	benergy = arga*arge;

	printf("fenergy %lf benergy %lf %f\n",fenergy,benergy,br);
	return (fenergy-benergy)/(2.0*h);
}

void do_force_nanotube_cos_cuttoff(int npoints,double* force,double* pos,double* energy,
		double* vel,double x1,double x2)
{
	int i,j;
	double dx,dy,dz,r,dot,expo,av,bonds,dudx;
	double qi,qj,u;
	double totalenergy,arga,darga,r2,arge,darge,pairforce,pairenergy;
	expo = 1.0;
	av = 0;
	bonds = 0;
	totalenergy = 0;
//	for(i=0;i<energydim;i++) {
//		energy[i]=0.0;
//	}
	//printf("C force zcutoff %lf \n",zcutoff);
	for(i=0;i<npoints;i++)
    {
		//if(pos[i*3+2]> x2){continue;}

    	for(j=i+1;j<npoints;j++)
    	{
    		//if(pos[j*3+2]> x2){continue;}

    		dx=pos[i*3]-pos[j*3];
			dy=pos[i*3+1]-pos[j*3+1];
			dz=pos[i*3+2]-pos[j*3+2]	;
			r2 = dx*dx + dy*dy + dz*dz;


    		r = sqrt(r2);
			av += r;
			bonds+=1.0;
			qi=1.0;
			qj=1.0;

			if(r<x1){
				pairenergy = qi*qj*1.0/(pow(r,expo));
				pairforce = qi*qj*-1.0*expo/pow(r,expo+1.0);
			}
			else if(r>x2){
				pairenergy=0.0;
				pairforce=0.0;
			}
			else
			{
				u = (r - x1)/(x2 - x1) *M_PI;

				arga = qi*qj*1.0/(pow(r,expo));
				arge = cos(u)/2.0 + 0.5;

				darga = qi*qj*-1.0*expo/pow(r,expo+1.0);
				dudx = 1.0/(x2 - x1) * M_PI;
				darge = -1.0/2.0*sin(u)*dudx;

				pairenergy = arga*arge;
				pairforce = darga*arge + arga*darge;
				//numerical = get_numerical(r,x1,x2,0.001);


				//numerical = get_numerical(r,x1,x2,0.001);

				//printf(" r %lf x1 %lf x2 %lf u %lf arge %lf darge %lf pairenergy %lf force %lf numer %lf \n", r,x1,x2,u,arge,darge,pairenergy,pairforce,numerical);

			}
			pairforce*=-1;


			totalenergy += pairenergy;

			energy[i] += (pairenergy)/2.0;
			energy[j] += (pairenergy)/2.0;

			force[i*3] += pairforce*(dx/r);
			force[i*3+1] += pairforce*(dy/r);
			force[i*3+2] += pairforce*(dz/r);
			force[j*3] -= pairforce*(dx/r);
			force[j*3+1] -= pairforce*(dy/r);
			force[j*3+2] -= pairforce*(dz/r);


    	}

    }

	FILE *f = fopen("testforce.txt","w");

	for(r=0.01;r<10;r+=0.01)
	    {
		if(r<x1){
			pairenergy = qi*qj*1.0/(pow(r,expo));
			pairforce = qi*qj*-1.0*expo/pow(r,expo+1.0);
		}
		else if(r>x2){
			pairenergy=0.0;
			pairforce=0.0;
		}
		else
		{
			u = (r - x1)/(x2 - x1) *M_PI;

			arga = qi*qj*1.0/(pow(r,expo));
			arge = cos(u)/2.0 + 0.5;

			darga = qi*qj*-1.0*expo/pow(r,expo+1.0);
			dudx = 1.0/(x2 - x1) * M_PI;
			darge = -1.0/2.0*sin(u)*dudx;

			pairenergy = arga*arge;
			pairforce = darga*arge + arga*darge;

			//numerical = get_numerical(r,x1,x2,0.001);

			//printf(" r %lf x1 %lf x2 %lf u %lf arge %lf darge %lf pairenergy %lf force %lf numer %lf \n", r,x1,x2,u,arge,darge,pairenergy,pairforce,numerical);
		}
		pairforce*=-1;
		fprintf(f, "%lf %lf %lf \n", r, pairenergy,pairforce);

	    }

	fclose(f);


	//printf("bonds %lf energy %lf\n",bonds,totalenergy);
    double maxf = -1000.0;

	//modify force
    for(i=0;i<npoints;i++)
    {
    	//if(pos[i*3+2]> 0.0){continue;}
    	dot=force[i*3]*pos[i*3];
    	dot+=force[i*3+1]*pos[i*3+1];
    	dot+=force[i*3+2]*pos[i*3+2];

    	force[i*3] = force[i*3]-dot*pos[i*3];
    	force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
    	force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];

    	if(abs(force[i*3])>maxf){
    		maxf=fabs(force[i*3]);
    	}
    	if(abs(force[i*3+1])>maxf){
    		maxf=fabs(force[i*3+1]);
    	}
    	if(abs(force[i*3+2])>maxf){
    		maxf=fabs(force[i*3+2]);
    	}
    }

}



void do_force_nanotube_erfc(int npoints,double* force,double* pos,double* energy,
		double* vel,double gamma,double zcutoff)
{
	int i,j;
	double dx,dy,dz,r,dot,expo,av,bonds;
	double qi,qj;
	double totalenergy,arga,darga,r2,arge,darge,totalforce;
	expo = 1.0;
	av = 0;
	bonds = 0;
	totalenergy = 0;
//	for(i=0;i<energydim;i++) {
//		energy[i]=0.0;
//	}
	
	//printf("C force zcutoff %lf \n",zcutoff);
	for(i=0;i<npoints;i++)
    {
		if(pos[i*3+2]> zcutoff){continue;}

    	for(j=i+1;j<npoints;j++)
    	{
    		if(pos[j*3+2]> zcutoff){continue;}

    		dx=pos[i*3]-pos[j*3];
			dy=pos[i*3+1]-pos[j*3+1];
			dz=pos[i*3+2]-pos[j*3+2]	;
			r2 = dx*dx + dy*dy + dz*dz;


    		r = sqrt(r2);
			av += r;
			bonds+=1.0;
			qi=1.0;
			qj=1.0;

			arga = qi*qj*1.0/(pow(r,expo));
			arge = gamma*erfc(r) ;

			totalenergy+= arga*arge;
			energy[i] += (arga*arge)/2.0;
			energy[j] += (arga*arge)/2.0;

			darga = qi*qj*-1.0*expo/pow(r,expo+1.0);
			darge = gamma*derfc(r);
			totalforce = darga*arge + arga*darge;

			totalforce*=-1;

			force[i*3] += totalforce*(dx/r);
			force[i*3+1] += totalforce*(dy/r);
			force[i*3+2] += totalforce*(dz/r);
			force[j*3] -= totalforce*(dx/r);
			force[j*3+1] -= totalforce*(dy/r);
			force[j*3+2] -= totalforce*(dz/r);


    	}

    }
	//printf("bonds %lf energy %lf\n",bonds,totalenergy);
    double maxf = -1000.0;

	//modify force
    for(i=0;i<npoints;i++)
    {
    	//if(pos[i*3+2]> 0.0){continue;}
    	dot=force[i*3]*pos[i*3];
    	dot+=force[i*3+1]*pos[i*3+1];
    	dot+=force[i*3+2]*pos[i*3+2];

    	force[i*3] = force[i*3]-dot*pos[i*3];
    	force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
    	force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];

    	if(abs(force[i*3])>maxf){
    		maxf=fabs(force[i*3]);
    	}
    	if(abs(force[i*3+1])>maxf){
    		maxf=fabs(force[i*3+1]);
    	}
    	if(abs(force[i*3+2])>maxf){
    		maxf=fabs(force[i*3+2]);
    	}
    }

}



void do_force_nanotube(int npoints,double* force,double* pos,double* energy,
		double* vel,double cutoff,double zcutoff)
{
	int i,j;
	double dx,dy,dz,r,dot,expo,av,bonds;
	double qi,qj;
	double totalenergy,arga,darga,r2,cutoff2;
	expo = 1.0;
	av = 0;
	bonds = 0;
	cutoff2 = cutoff*cutoff;
	totalenergy = 0;
//	for(i=0;i<energydim;i++) {
//		energy[i]=0.0;
//	}
	
	//printf("C force zcutoff %lf \n",zcutoff);
	for(i=0;i<npoints;i++)
    {
		if(pos[i*3+2]> zcutoff){continue;}

    	for(j=i+1;j<npoints;j++)
    	{
    		if(pos[j*3+2]> zcutoff){continue;}

    		dx=pos[i*3]-pos[j*3];
			dy=pos[i*3+1]-pos[j*3+1];
			dz=pos[i*3+2]-pos[j*3+2]	;
			r2 = dx*dx + dy*dy + dz*dz;

    		if(r2<cutoff2)
    		{
    			r = sqrt(r2);
    			av += r;
    			bonds+=1.0;
    			qi=1.0;
    			qj=1.0;
//    			if(pos[j*3+2]>zcutoff )
//    			{
////    				expo=1.0 + (pos[j*3+2]-zcutoff)*0.5 ;
//    				expo=0.2;
//
//    			}
////    			else if(pos[i*3+2]>zcutoff)
////				{
////					expo=1.0 + (pos[i*3+2]-zcutoff)*0.5 ;
////					expo=2.0;
////				}
//    			else
//    			{

//    				if(pos[i*3+2]<0.0 )
//    				{
//    					printf("i %d j %d cap r dist %lf\n",i,j,r);
//    				}
    				//expo=1.0;
    			//}
    				arga = pow(r,expo);
					darga = qi*qj*expo/pow(r,expo+1.0);
					totalenergy += qi*qj*1.0/arga;
					energy[i] += (qi*qj*1.0/arga)/2.0;
					energy[j] += (qi*qj*1.0/arga)/2.0;
					force[i*3] += darga*(dx/r);
					force[i*3+1] += darga*(dy/r);
					force[i*3+2] += darga*(dz/r);
					force[j*3] -= darga*(dx/r);
					force[j*3+1] -= darga*(dy/r);
					force[j*3+2] -= darga*(dz/r);
    			//}

    		}

    	}

    }
	//printf("bonds %lf energy %lf\n",bonds,totalenergy);
    double maxf = -1000.0;

	//modify force
    for(i=0;i<npoints;i++)
    {
    	//if(pos[i*3+2]> 0.0){continue;}
    	dot=force[i*3]*pos[i*3];
    	dot+=force[i*3+1]*pos[i*3+1];
    	dot+=force[i*3+2]*pos[i*3+2];

    	force[i*3] = force[i*3]-dot*pos[i*3];
    	force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
    	force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];

    	if(abs(force[i*3])>maxf){
    		maxf=fabs(force[i*3]);
    	}
    	if(abs(force[i*3+1])>maxf){
    		maxf=fabs(force[i*3+1]);
    	}
    	if(abs(force[i*3+2])>maxf){
    		maxf=fabs(force[i*3+2]);
    	}
    }

}

void remove_radial_component__of_force(int npoints,double* force,double* pos)
{
	int i;
	double dot;
	//double maxf = -1000.0;

	//modify force
	for(i=0;i<npoints;i++)
	{
		//if(pos[i*3+2]> 0.0){continue;}
		dot=force[i*3]*pos[i*3];
		dot+=force[i*3+1]*pos[i*3+1];
		dot+=force[i*3+2]*pos[i*3+2];

		force[i*3] = force[i*3]-dot*pos[i*3];
		force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
		force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];

//		if(abs(force[i*3])>maxf){
//			maxf=fabs(force[i*3]);
//		}
//		if(abs(force[i*3+1])>maxf){
//			maxf=fabs(force[i*3+1]);
//		}
//		if(abs(force[i*3+2])>maxf){
//			maxf=fabs(force[i*3+2]);
//		}
	}
}

void force_on_cap_atoms_in_tube(int ncap,double* force,double* pos,
								double* energy,double k)
{
	int i;
	double expo;
	expo = 1.0;
	//printf("C force_on_cap_atoms_in_tube\n");
	for(i=0;i<ncap;i++)
		{
			if(pos[i*3+2]>0.0)
			{

				energy[i] += (1.0/expo)*k*pow(pos[i*3+2],expo+1);
				//printf("b adding force %lf\n",force[i*3+2] );
				force[i*3+2] -= k*pow(pos[i*3+2],expo);
				//printf("a adding force %lf\n",force[i*3+2] );
				//printf("adding force %lf\n",k*pos[i*3+2]);
			}
		}
}

void thomson_force_call(int npoints,double* force,double* pos,
						double* energy,double* vel,double* freeflagspos,
						double expo,double cutoff,double zcutoff)
{

	int i,j;
	double dx,dy,dz,r;
	double qi,qj;
	double totalenergy,arga,darga,r2,cutoff2;
	//expo = 1.0;
	cutoff2 = cutoff*cutoff;
	totalenergy = 0;
	//printf("C force zcutoff %lf \n",zcutoff);
	for(i=0;i<npoints;i++)
	{
		if(pos[i*3+2]> zcutoff && freeflagspos[i*3+2]==0){continue;}

		for(j=i+1;j<npoints;j++)
		{
			if(pos[j*3+2]> zcutoff && freeflagspos[j*3+2]==0){continue;}

			dx=pos[i*3]-pos[j*3];
			dy=pos[i*3+1]-pos[j*3+1];
			dz=pos[i*3+2]-pos[j*3+2]	;
			r2 = dx*dx + dy*dy + dz*dz;

			if(r2<cutoff2)
			{
				r = sqrt(r2);
				qi=1.0;
				qj=1.0;

				arga = pow(r,expo);
				darga = qi*qj*expo/pow(r,expo+1.0);
				totalenergy += qi*qj*1.0/arga;
				energy[i] += (qi*qj*1.0/arga)/2.0;
				energy[j] += (qi*qj*1.0/arga)/2.0;
				force[i*3] += darga*(dx/r);
				force[i*3+1] += darga*(dy/r);
				force[i*3+2] += darga*(dz/r);

				force[j*3] -= darga*(dx/r);
				force[j*3+1] -= darga*(dy/r);
				force[j*3+2] -= darga*(dz/r);

			}

		}

	}

	//remove_radial_component__of_force(npoints,force,pos);
//
//	//printf("bonds %lf energy %lf\n",bonds,totalenergy);
//	double maxf = -1000.0;
//
//	//modify force
//	for(i=0;i<npoints;i++)
//	{
//		//if(pos[i*3+2]> 0.0){continue;}
//		dot=force[i*3]*pos[i*3];
//		dot+=force[i*3+1]*pos[i*3+1];
//		dot+=force[i*3+2]*pos[i*3+2];
//
//		force[i*3] = force[i*3]-dot*pos[i*3];
//		force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
//		force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];
//
//		if(abs(force[i*3])>maxf){
//			maxf=fabs(force[i*3]);
//		}
//		if(abs(force[i*3+1])>maxf){
//			maxf=fabs(force[i*3+1]);
//		}
//		if(abs(force[i*3+2])>maxf){
//			maxf=fabs(force[i*3+2]);
//		}
//	}

}







void do_force_no_rdf(int npoints,double* force,double* pos,double* energy,double* vel,double cutoff)
{
	int i,j;
	double dx,dy,dz,r,dot,expo;
	double qi,qj,vartstep;
	double totalenergy,arga,darga,r2,cutoff2,maxf;
	expo = 1.0;
	cutoff2 = cutoff*cutoff;
	totalenergy = 0;
//	for(i=0;i<energydim;i++) {
//		energy[i]=0.0;
//	}
	vartstep = 1.0;
	//printf("C force zcutoff %lf \n",zcutoff);
	for(i=0;i<npoints;i++)
    {

    	for(j=i+1;j<npoints;j++)
    	{
    		dx=pos[i*3]-pos[j*3];
			dy=pos[i*3+1]-pos[j*3+1];
			dz=pos[i*3+2]-pos[j*3+2]	;
			r2 = dx*dx + dy*dy + dz*dz;

    		if(r2<cutoff2)
    		{
    			r = sqrt(r2);
    			qi=1.0;
    			qj=1.0;
				arga = (qi*qj*1.0)/pow(r,expo);
				darga = qi*qj*expo/pow(r,expo+1.0);
				totalenergy += arga;
				energy[i] += arga/2.0;
				energy[j] += arga/2.0;
				force[i*3] += darga*(dx/r);
				force[i*3+1] += darga*(dy/r);
				force[i*3+2] += darga*(dz/r);
				force[j*3] -= darga*(dx/r);
				force[j*3+1] -= darga*(dy/r);
				force[j*3+2] -= darga*(dz/r);


    		}

    	}

    }
    maxf = -1000.0;
	//modify force
    for(i=0;i<npoints;i++)
    {

    	dot=force[i*3]*pos[i*3];
    	dot+=force[i*3+1]*pos[i*3+1];
    	dot+=force[i*3+2]*pos[i*3+2];

    	force[i*3] = force[i*3]-dot*pos[i*3];
    	force[i*3+1] = force[i*3+1]-dot*pos[i*3+1];
    	force[i*3+2] = force[i*3+2]-dot*pos[i*3+2];

    	if(abs(force[i*3])>maxf){
    		maxf=fabs(force[i*3]);
    	}
    	if(abs(force[i*3+1])>maxf){
    		maxf=fabs(force[i*3+1]);
    	}
    	if(abs(force[i*3+2])>maxf){
    		maxf=fabs(force[i*3+2]);
    	}
    }

}

void scale_rad(int npoints, double* pos,double reqrad, int isHemisphere, double length)
{
	double r,magxy;
	int i;
	for(i=0;i<npoints;i++)
    {
			if(isHemisphere==0)
			{
				r = sqrt(pow(pos[i*3],2) + pow(pos[i*3+1],2) +pow(pos[i*3+2],2));

				pos[i*3] = (pos[i*3]/r) * reqrad;
				pos[i*3+1] = (pos[i*3+1]/r) * reqrad;
				pos[i*3+2] = (pos[i*3+2]/r) * reqrad;
			}
			else
			{
				if(pos[i*3+2]>0 && pos[i*3+2] < length)
				{
				magxy=sqrt(pow(pos[i*3],2) + pow(pos[i*3+1],2));
				pos[i*3] = (pos[i*3]/magxy) * reqrad;
				pos[i*3+1] = (pos[i*3+1]/magxy) * reqrad;
				pos[i*3+2] = pos[i*3+2] * reqrad;
				//printf(" C scaling to hemisphere %d\n",i);
				}
				else
				{
				if(pos[i*3+2]<=0){
					r = sqrt(pow(pos[i*3],2) + pow(pos[i*3+1],2) +pow(pos[i*3+2],2));
					//printf(" C scaling to hemisphere Z<0 %d r %lf\n",i,r);
					pos[i*3] = (pos[i*3]/r) * reqrad;
					pos[i*3+1] = (pos[i*3+1]/r) * reqrad;
					pos[i*3+2] = (pos[i*3+2]/r) * reqrad;
					}
				else
					{

					r = sqrt(pow(pos[i*3],2) + pow(pos[i*3+1],2) +pow((pos[i*3+2]-length),2));
					//printf(" C scaling to hemisphere Z>Length%d r %lf\n",i,r);
					pos[i*3] = (pos[i*3]/r) * reqrad;
					pos[i*3+1] = (pos[i*3+1]/r) * reqrad;
					pos[i*3+2] = ((pos[i*3+2]-length)/r) *reqrad + length*reqrad;

					}
				}
			}
    }

}

double do_gauss_force(int npoints,double* force,double* pos,double* gpos, double width, double height )
{
	int i;
	double del,coeff,exponent,genergy;

	coeff = 1.0/(2.0*width*width);

	exponent = 0.0;

	for(i=0;i<npoints;i++)
    {
		del = pos[i] - gpos[i];
		//printf(" del %lf %lf %lf\n",del,pos[i],gpos[i]);
		exponent += del*del*coeff;
    }
	genergy = height*exp(-1.0*exponent);

	for(i=0;i<npoints;i++)
    {
    	del = pos[i] - gpos[i];
    	force[i] -= -2.0*coeff*del*genergy;
    }
    //printf("g energy %lf coeff %lf exponent %lf\n",genergy,coeff,exponent);
	return genergy;
}

void calc_carbon_carbon_neb_list(int Nc,
						  	     double* Cpos,
						  	     int* nebs,
						  	   double* nebdist)
{
	int i,j,d;
	double xi,yi,zi;
	double xj,yj,zj,r2;
	//double nebdist[Nc*3];

	for (i = 0; i < Nc; i++){
		for (d = 0; d < 3; d++){
			nebdist[i*3+d] = 10000.0;
		}
	}

	for (i = 0; i < Nc; i++)
		{
		xi = Cpos[i*3];
		yi = Cpos[i*3+1];
		zi = Cpos[i*3+2];

		for (j = i+1; j < Nc; j++)
			{
			xj = Cpos[j*3];
			yj = Cpos[j*3+1];
			zj = Cpos[j*3+2];

			r2 = (xi-xj)*(xi-xj);
			r2 += (yi-yj)*(yi-yj);
			r2 += (zi-zj)*(zi-zj);


			if(r2<=nebdist[i*3+0])
			{
				nebs[i*3+2] = nebs[i*3+1];
				nebs[i*3+1] = nebs[i*3+0];
				nebs[i*3+0] = j;

				nebdist[i*3+2] = nebdist[i*3+1];
				nebdist[i*3+1] = nebdist[i*3+0];
				nebdist[i*3+0] = r2;
			}
			if(r2 > nebdist[i*3+0] && r2<=nebdist[i*3+1])
			{
				nebs[i*3+2] = nebs[i*3+1];
				nebs[i*3+1] = j;

				nebdist[i*3+2] = nebdist[i*3+1];
				nebdist[i*3+1] = r2;

			}
			if(r2 > nebdist[i*3+1] && r2<=nebdist[i*3+2])
			{
				nebs[i*3+2] = j;
				nebdist[i*3+2] = r2;
			}


			if(r2<=nebdist[j*3+0])
			{
				nebs[j*3+2] = nebs[j*3+1];
				nebs[j*3+1] = nebs[j*3+0];
				nebs[j*3+0] = i;

				nebdist[j*3+2] = nebdist[j*3+1];
				nebdist[j*3+1] = nebdist[j*3+0];
				nebdist[j*3+0] = r2;
			}
			if(r2 > nebdist[j*3+0] && r2<=nebdist[j*3+1])
			{
				nebs[j*3+2] = nebs[j*3+1];
				nebs[j*3+1] = i;

				nebdist[j*3+2] = nebdist[j*3+1];
				nebdist[j*3+1] = r2;

			}
			if(r2 > nebdist[j*3+1] && r2<=nebdist[j*3+2])
			{
				nebs[j*3+2] = i;
				nebdist[j*3+2] = r2;
			}

			}
		}
//	for (i = 0; i < 10; i++)
//		{
//		printf("carbon atom %d carbon nebs %d %d %d \n",i,nebs[i*3+0],nebs[i*3+1],nebs[i*3+2] );
//		printf("carbon atom %d carbon nebs dists %lf %lf %lf \n",i,nebdist[i*3+0],nebdist[i*3+1],nebdist[i*3+2] );
//		}

}

int get_carbon_bond_angles(double* angles,int Nc,double *Cpos)
{
	double dp,theta,pi;
	int i,j,k,d,e,count;
	int *cc_nebs;
	double *cc_nebdists;
	double ji[3],ki[3],nullv[3];
	cc_nebs = (int*) malloc(3*Nc*sizeof (int));
	cc_nebdists = (double*) malloc(3*Nc*sizeof (double));
	calc_carbon_carbon_neb_list(Nc,Cpos,cc_nebs,cc_nebdists);
	nullv[0] = 0.0;
	nullv[1] = 0.0;
	nullv[2] = 0.0;
	pi = 4.0*atan(1.0);

	count = 0;
	for(i=0;i<Nc;i++)
		{
		for(d=0;d<3;d++)
		{
			j = cc_nebs[i*3+d];
			//if(j<=i){continue;}

			for(e=d+1;e<3;e++)
					{
					k = cc_nebs[i*3+e];
					//if(k<=j){continue;}


					ji[0] = Cpos[j*3]-Cpos[i*3];
					ji[1] = Cpos[j*3+1]-Cpos[i*3+1];
					ji[2] = Cpos[j*3+2]-Cpos[i*3+2];

					ki[0] = Cpos[k*3]-Cpos[i*3];
					ki[1] = Cpos[k*3+1]-Cpos[i*3+1];
					ki[2] = Cpos[k*3+2]-Cpos[i*3+2];

					dp = dot(ji,ki);
					theta =	acos(dp/(magnitude_diff(ji,nullv)*magnitude_diff(ki,nullv)));
					theta = theta * 180.0 / pi;
					//printf("i %d j %d k %d theta %lf \n",i,j,k,theta);
					angles[count] = theta;
					count++;
					}


		}

		}
return count;
}


int calc_carbon_bonds(int Nc,
					   double *Cpos,
					   int *bonds,
					   double cutoff)
{
	int i,j,NBonds,neb;

	int *cc_nebs;
	double *cc_nebdists;
	cc_nebs = (int*) malloc(3*Nc*sizeof (int));
	cc_nebdists = (double*) malloc(3*Nc*sizeof (double));
	calc_carbon_carbon_neb_list(Nc,Cpos,cc_nebs,cc_nebdists);

	NBonds = 0;
	for(i=0;i<Nc;i++)
	{
		for(j=0;j<3;j++)
		{
			neb=cc_nebs[i*3+j];
			//printf("neb %d dist %lf cutf %lf\n",neb,cc_nebdists[i*3+j],cutoff);
			if(cc_nebdists[i*3+j]>cutoff*cutoff)
				{

				continue;
				}

//			bonds[NBonds*6] = Cpos[i*3];
//			bonds[NBonds*6+1] = Cpos[i*3+1];
//			bonds[NBonds*6+2] = Cpos[i*3+2];
//			bonds[NBonds*6+3] = Cpos[neb*3];
//			bonds[NBonds*6+4] = Cpos[neb*3+1];
//			bonds[NBonds*6+5] = Cpos[neb*3+2];

			bonds[NBonds*2] = i;
			bonds[NBonds*2+1] = neb;

			NBonds++;


		}
	}
	//printf("C Nbonds %d \n",NBonds);
	free(cc_nebs);
	return NBonds;
}

void calc_thomson_carbon_neb_list(int Nt,
		  	  	  	  	  	  	  int Nc,
		  	  	  	  	  	  	  int* tc_nebs,
		  	  	  	  	  	  	  double* Tpos,
		  	  	  	  	  	  	  double* Cpos)

{
	//printf("BOAHBKASD\n");
	int i,j;
	double xt,yt,zt,xc,yc,zc,r2,rmin;
	for (i = 0; i < Nt; i++)
			{
			//printf("i point %d \n",i);
			xt = Tpos[i*3];
			//printf("x point %lf \n",xt);
			yt = Tpos[i*3+1];
			zt = Tpos[i*3+2];
			rmin = 100000.0;

			for (j = 0; j < Nc; j++)
					{
					xc = Cpos[j*3];
					yc = Cpos[j*3+1];
					zc = Cpos[j*3+2];

					r2 = (xt-xc)*(xt-xc);
					r2 += (yt-yc)*(yt-yc);
					r2 += (zt-zc)*(zt-zc);
					if(r2<rmin)
					{
						tc_nebs[i] = j;
						rmin  = r2;
						//printf("thomson point %d carbon neb %d \n",i,tc_nebs[i] );
					}

					}
			}
//	for (i = 0; i < 10; i++)
//			{
//			printf("thomson point %d carbon neb %d \n",i,tc_nebs[i] );
//			}

}


void get_closest_pair(int Tp,
					  int Cp,
		              double* Tpos,
		              int* cc_nebs,
		              double* Cpos,
		              int* out_pair)
{
	int j,CNeb,neb0,neb1;
	double xt,yt,zt,xc,yc,zc,r2;
	double rmin0,rmin1;
	xt = Tpos[Tp*3];
	yt = Tpos[Tp*3+1];
	zt = Tpos[Tp*3+2];
	rmin0 = 10000.0;
	rmin1 = 10000.0;
      neb0 = -1;
      neb1 = -1;
	for (j = 0; j < 3; j++)
	{
		CNeb = cc_nebs[Cp*3 + j];

		xc = Cpos[CNeb*3];
		yc = Cpos[CNeb*3+1];
		zc = Cpos[CNeb*3+2];
		r2 = (xt-xc)*(xt-xc);
		r2 += (yt-yc)*(yt-yc);
		r2 += (zt-zc)*(zt-zc);
		//printf("getting closest pair to carbon atom %d checking %d dist %lf %d %d \n",Cp,CNeb,r2,neb0,neb1);
		if(r2<=rmin0)
		{
			rmin1 = rmin0;
			neb1 = neb0;
			rmin0 = r2;
			neb0 = CNeb;
		}
		if(r2> rmin0 && r2<=rmin1)
		{
			rmin1 = r2;
			neb1 = CNeb;
		}

	}
	out_pair[0]=neb0;
	out_pair[1]=neb1;
}

int get_ring(int Tp,
			 int firstneb,
			 int* cc_nebs,
			 double* Tpos,
			 double* Cpos,
			 int* ring_indexes)
{
	double xt,yt,zt;
	int i,lastneb,ringcount,currentneb,search;
	int* out_pair;
	out_pair = (int*) malloc(2*sizeof (int));

	xt = Tpos[Tp*3];
	yt = Tpos[Tp*3+1];
	zt = Tpos[Tp*3+2];

	ring_indexes[0] = firstneb;

	lastneb = -1;
	ringcount = 1;
	currentneb = firstneb;
	search=1;
	while(search==1)
	{

		get_closest_pair(Tp,currentneb,Tpos,cc_nebs,Cpos,out_pair);
		printf("thomson point %d currentneb %d closest pair %d,%d %d \n",Tp,currentneb,out_pair[0],out_pair[1],lastneb);

		if(out_pair[0] == lastneb)
		{
			lastneb = currentneb;
			currentneb = out_pair[1];
		}
		else
		{
			lastneb = currentneb;
			currentneb = out_pair[0];
		}
//		if(currentneb==firstneb && ringcount>1)
//		{
//			search=0;
//		}

		for (i = 0; i < ringcount; i++)
			{
				if(currentneb==ring_indexes[i])
				{
					search=0;
				}
			}

		if(search==1)
			{
			ring_indexes[ringcount] = currentneb;
			ringcount++;
			}


	}
	free(out_pair);
	return ringcount;
}


void calc_bonding_polygons_using_ring(int Nt,
						   int Nc,
						   double * Tpos,
						   double * Cpos,
						   double * bondLengths,
						   double bondScaleFactor,
						   int maxBondingPolygonVerts,
						   double * bondingPolygonPoints,
						   int * bondingPolygonPointsCount,
						   int * polyCount

						   )
{
	int i,j,firstneb;
	int cindex,nring;

	double xt,yt,zt,xc,yc,zc;

	//carbon-carbon nebs (assuming 3 fold)
	int *cc_nebs;
	double *cc_nebdists;
	int* tc_nebs;
	int* ring_indexes;
	cc_nebs = (int*) malloc(3*Nc*sizeof (int));
	cc_nebdists = (double*) malloc(3*Nc*sizeof (double));
	tc_nebs = (int*) malloc(Nt*sizeof (int));
	ring_indexes = (int*) malloc(maxBondingPolygonVerts*sizeof (int));

	//[3*Nt];
	//closest carbon atom to a thomson point
	//int cc_nebs[3*Nt];
	//int tc_nebs[Nt];
	//int ring_indexes[maxBondingPolygonVerts];

	calc_carbon_carbon_neb_list(Nc,Cpos,cc_nebs,cc_nebdists);
	printf("BLAH\n");
	calc_thomson_carbon_neb_list(Nt,Nc,tc_nebs,Tpos,Cpos);

	for (i = 0; i < Nt; i++)
	{
		xt = Tpos[i*3];
		yt = Tpos[i*3+1];
		zt = Tpos[i*3+2];

		firstneb = tc_nebs[i];

		nring = get_ring(i,firstneb,cc_nebs,Tpos,Cpos,ring_indexes);

		printf("thomson point %d nring %d \n",i,nring );
		for (j = 0; j < nring; j++)
		{
			cindex = ring_indexes[j];
			xc = Cpos[cindex*3];
			yc = Cpos[cindex*3+1];
			zc = Cpos[cindex*3+2];
			bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +0] = xc;
			bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +1] = yc;
			bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +2] = zc;
			bondingPolygonPointsCount[i]++;
		}

		polyCount[bondingPolygonPointsCount[i]]++;

	}
	free(cc_nebs);
	free(tc_nebs);
	free(ring_indexes);

}


int find_common_neb(int inneb,double * Nebpos,int * nebs,int oldneb, int nnebs)
{
	double xNeb,yNeb,zNeb,r2;
	double xj,yj,zj,rmin2;
	int j,nebout,neb;

	xNeb = Nebpos[inneb*3];
	yNeb = Nebpos[inneb*3+1];
	zNeb = Nebpos[inneb*3+2];

      nebout = -1;
	rmin2 = 1000000;
	for (j = 0; j < nnebs; j++)
		{
		neb = nebs[j];
		if(neb==oldneb || neb==inneb){continue;}

		xj = Nebpos[neb*3];
		yj = Nebpos[neb*3+1];
		zj = Nebpos[neb*3+2];

		r2 = (xj-xNeb)*(xj-xNeb);
		r2 += (yj-yNeb)*(yj-yNeb);
		r2 += (zj-zNeb)*(zj-zNeb);

		if(r2 < rmin2)
		{
			nebout=neb;
			rmin2 = r2;
		}
	}

	return nebout;
}

int check_if_nebs(int neb0,int neb1,int* cc_nebs)
{
	//check if 0 and 1 are nebs return -1 if true or the common neb if not.
	//if > 1 neb inbetween return true anyway
	int c0,c1,cneb0,cneb1,common;
	common=-1;

	for (c0 = 0; c0 < 3; c0++)
	{
		cneb0 = cc_nebs[neb0*3+c0];
		if(cneb0==neb1){
			return -1;
		}
		for (c1 = 0; c1 < 3; c1++)
		{
			//printf("cneb0 %d cneb1 %d \n",cneb0,cneb1);
			cneb1 = cc_nebs[neb1*3+c1];
			if(cneb1==neb0){
				return -1;
			}

			if(cneb0==cneb1){
				common=cneb0;
				return common;
			}
		}
	}
	return -1;
}




int get_extra_neb(int nebcount,int* nebs, int* cc_nebs)
{
	int j,k,l,neb0,neb1,ret;

	for (j = 0; j < nebcount; j++)
	{
		neb0 = nebs[j];
		for (k = j+1; k < nebcount; k++)
		{
			neb1 = nebs[k];
			if(neb0==neb1){continue;}

			ret = check_if_nebs(neb0,neb1,cc_nebs);
			if(ret==-1){continue;}

			int inlist=0;
			for (l = 0; l < nebcount; l++)
			{
				if(nebs[l]==ret){
					inlist=1;
				}
			}
			if(inlist==0){
				return ret;
			}
		}

	}
	return -1;
}

void calc_bonding_polygons(int Nt,
						   int Nc,
						   double * Tpos,
						   double * Cpos,
						   double * bondLengths,
						   double bondScaleFactor,
						   int maxBondingPolygonVerts,
						   double * bondingPolygonPoints,
						   int * bondingPolygonPointsCount,
						   int * bondingPolygonIndexes,
						   int * polyCount
						   )
{
	int i,j,k,nebid,ret;
	int neb,neb2,oldneb;

	double xt,yt,zt,xc,yc,zc,r2,b2;
	int *cc_nebs;
	double *cc_nebdists;

	cc_nebs = (int*) malloc(3*Nc*sizeof (int));
	cc_nebdists = (double*) malloc(3*Nc*sizeof (double));
	calc_carbon_carbon_neb_list(Nc,Cpos,cc_nebs,cc_nebdists);

	double vec1[3],vec2[3],nullv[3],dp,mag1,mag2;
	nullv[0] = 0.0;
	nullv[1] = 0.0;
	nullv[2] = 0.0;

	for (i = 0; i < Nt; i++)
	{
		xt = Tpos[i*3];
		yt = Tpos[i*3+1];
		zt = Tpos[i*3+2];
		b2 = bondLengths[i]*bondLengths[i]*bondScaleFactor*bondScaleFactor;

		int tempnebs[maxBondingPolygonVerts];
		for (j = 0; j < Nc; j++)
			{
			xc = Cpos[j*3];
			yc = Cpos[j*3+1];
			zc = Cpos[j*3+2];

			r2 = (xt-xc)*(xt-xc);
			r2 += (yt-yc)*(yt-yc);
			r2 += (zt-zc)*(zt-zc);

			if(r2<b2){

			//we have a carbon atom j neb to our thomson point i

				//check if lies behind another point
				vec1[0] = xc-xt;
				vec1[1] = yc-yt;
				vec1[2] = zc-zt;
				int ignore=0;
				for (k = 0; k < bondingPolygonPointsCount[i]; k++)
				{
					vec2[0] = Cpos[tempnebs[k]*3]-xt;
					vec2[1] = Cpos[tempnebs[k]*3+1]-yt;
					vec2[2] = Cpos[tempnebs[k]*3+2]-zt;
					mag2 = magnitude_diff(vec2,nullv);
					mag1 = magnitude_diff(vec1,nullv);
					dp = dot(vec1,vec2)/(mag1*mag2);
					//printf("dp %lf vec1 %lf vec2 %lf\n",dp,magnitude_diff(vec1,nullv),magnitude_diff(vec2,nullv));
					if(dp>0.9)
					{
						if(dot(vec1,vec2)/mag2 > mag2){ignore=1;}
						else{
							nebid = k;
							tempnebs[k] = j;
							//bondingPolygonPointsCount[i]++;
							ignore=1;
						}
					}
				}
				if(ignore==1){continue;}

				nebid = bondingPolygonPointsCount[i];
				tempnebs[nebid] = j;
////				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + nebid*3 +0] = xc;
////				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + nebid*3 +1] = yc;
////				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + nebid*3 +2] = zc;
				bondingPolygonPointsCount[i]++;
			}

			}

		//check if points missed by cutoff b2. We check the neighbourhood of each
		// point in the polygon. if 2 points have shared neb that isnt in the polygon
		// we add it.
		int checkNebs=0;
		if(checkNebs==1){
			ret = get_extra_neb(bondingPolygonPointsCount[i],tempnebs,cc_nebs);
			if(ret!=-1)
			{
				printf("%d extra %d\n",i,ret);
				tempnebs[bondingPolygonPointsCount[i]] = ret;
				bondingPolygonPointsCount[i]++;
			}
		}

		//printf("extra %d\n",extra);
		//bondingPolygonPointsCount[i]+=extra;

		//reorder clockwise
		oldneb=-1;
		neb = tempnebs[0];
		xc = Cpos[neb*3];
		yc = Cpos[neb*3+1];
		zc = Cpos[neb*3+2];
		bondingPolygonPoints[i*maxBondingPolygonVerts*3 + 0*3 +0] = xc;
		bondingPolygonPoints[i*maxBondingPolygonVerts*3 + 0*3 +1] = yc;
		bondingPolygonPoints[i*maxBondingPolygonVerts*3 + 0*3 +2] = zc;
		bondingPolygonIndexes[i*maxBondingPolygonVerts + 0] = neb;
		//printf("First Neb %d %lf %lf %lf \n",neb,xc,yc,zc);
		for (j = 1; j < bondingPolygonPointsCount[i]; j++)
			{


				neb2 = find_common_neb(neb,Cpos,tempnebs,oldneb,bondingPolygonPointsCount[i]);
				oldneb = neb;
				neb=neb2;
				xc = Cpos[neb*3];
				yc = Cpos[neb*3+1];
				zc = Cpos[neb*3+2];
				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +0] = xc;
				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +1] = yc;
				bondingPolygonPoints[i*maxBondingPolygonVerts*3 + j*3 +2] = zc;
				bondingPolygonIndexes[i*maxBondingPolygonVerts + j] = neb;

				//printf("%d Neb %d %lf %lf %lf \n",j,neb,xc,yc,zc);

			}
		polyCount[bondingPolygonPointsCount[i]]++;
	}
	free(cc_nebs);
//	for (i = 0; i < maxBondingPolygonVerts; i++)
//		{
//		printf(" N %d-agons %d\n",i,polyCount[i]);
//		}
}







void setup_random_points_on_sphere(int npoints,
						  int seed,
						  int isHemisphere,
						  double rad,
						  double * pos
						)
{
	int found,assigned,tooclose,i,a;
	double x,y,z,w,t,pi,r,zo;

	pi = 4.0*atan(1.0);
	srand(seed);
	assigned=0;
	if(isHemisphere==1){
		zo = 1.0;
	}
	else{
		zo = 2.0;
	}
	//printf("ZO %lf\n",zo);
	for (i = 0; i < npoints; i++)
	{
            found=0;
            z = (zo * ((double)rand()/(double)RAND_MAX) - 1.0)*rad;
            t = 2.0 * pi * ((double)rand()/(double)RAND_MAX);
            w = sqrt( rad*rad - z*z );
            x = w * cos( t );
            y = w * sin( t );
            if(assigned>0){
                while(found==0){
                    if(z<0.999){z+=0.001;}
                    else{z-=0.001;}
                    if(t<1.999 * pi){t+=0.001;}
                    else{t-=0.001;}

                    w = sqrt( rad*rad - z*z );
                    x = w * cos( t );
                    y = w * sin( t );

                    //printf("mag r %lf", sqrt(x*x + y*y +z*z));
                    tooclose = 0;
                    for (a = 0; a < assigned; a++){
                        r = (x - pos[a*3])*(x - pos[a*3]);
                        r += (y - pos[a*3+1])*(y - pos[a*3+1]);
                        r += (z - pos[a*3+2])*(z - pos[a*3+2]);
                        //r = sqrt(r)
                        //print "r",r
                        if(r<(0.005*0.005)){tooclose=1;}
                    }
                    if(tooclose==0){found=1;}
                }
            }
            pos[i*3] = x;
            pos[i*3+1] = y;
            pos[i*3+2] = z;

            assigned+=1;
	}
}
