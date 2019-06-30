// gmsh -2 -format msh mesh.geo
// gmsh -2 -refine 2 mesh.msh
// gmsh -2 -format vtk mesh.msh
// meshio-convert mesh.msh mesh.e
// python e2dfm.py

ls = 1;

oc_w = 60.0; // um
oc_h = 60.0; // um
ba_w = 20.0; // um
ba_h = 20.0; // um
ri_w = 1.0; // um
ri_h = 10.0; // um
ri_s = 1.0; // mesh size in river

oc = (oc_w - ba_w)*0.5;
ba = (ba_w - ri_w)*0.5;

Point(1) = {0, 0, 0, ls};
Point(2) = {oc, 0, 0, ls};
Point(3) = {oc, oc_h, 0, ls};
Point(4) = {0, oc_h, 0, ls};

Point(5) = {oc + ba_w, 0, 0, ls};
Point(6) = {oc + ba_w, oc_h, 0, ls};

Point(7) = {oc_w, 0, 0, ls};
Point(8) = {oc_w, oc_h, 0, ls};

Point(9) = {oc + ba, oc_h + ba_h, 0, ls};
Point(10) = {oc + ba_w - ba, oc_h + ba_h, 0, ls};

Point(11) = {oc + ba, oc_h + ba_h + ri_h, 0, ls};
Point(12) = {oc + ba_w - ba, oc_h + ba_h + ri_h, 0, ls};


Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

Line(5) = {2, 5};
Line(6) = {5, 6};
Line(7) = {6, 3};
Line(8) = {3, 2};
Curve Loop(2) = {5, 6, 7, 8};
Plane Surface(2) = {2};

Line(9) = {5, 7};
Line(10) = {7, 8};
Line(11) = {8, 6};
Line(12) = {6, 5};
Curve Loop(3) = {9, 10, 11, 12};
Plane Surface(3) = {3};

Line(13) = {3, 6};
Line(14) = {6, 10};
Line(15) = {10, 9};
Line(16) = {9, 3};
Curve Loop(4) = {13, 14, 15, 16};
Plane Surface(4) = {4};

Line(17) = {9, 10};
Line(18) = {10, 12};
Line(19) = {12, 11};
Line(20) = {11, 9};
Curve Loop(5) = {17, 18, 19, 20};
Plane Surface(5) = {5};

For i In {1:5}
Transfinite Surface {i};
EndFor

Transfinite Curve {20, 18} = Ceil(ri_h/ri_s) Using Progression 1;

RefineMesh;
Coherence;
Mesh.Smoothing = 40;

Mesh.Algorithm = 8; // Delaunay for quads
Mesh.SubdivisionAlgorithm = 1;

Recombine Surface {1, 2, 3, 4, 5};
Physical Surface(1) = {1, 2, 3, 4, 5};
