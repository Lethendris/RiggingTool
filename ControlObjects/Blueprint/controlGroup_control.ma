//Maya ASCII 2025ff03 scene
//Name: controlGroup_control.ma
//Last modified: Sat, Jun 14, 2025 08:44:37 AM
//Codeset: 1252
requires maya "2025ff03";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2025";
fileInfo "version" "2025";
fileInfo "cutIdentifier" "202407121012-8ed02f4c99";
fileInfo "osv" "Windows 11 Pro v2009 (Build: 26100)";
fileInfo "UUID" "AE2EFEF5-4856-D24D-E800-688EEBC29437";
createNode transform -n "controlGroup_control";
	rename -uid "CD57BFB1-4619-D90E-00FA-D19E817F2DAB";
createNode mesh -n "controlGroup_controlShape" -p "controlGroup_control";
	rename -uid "79D92E0F-4AF9-02C1-E875-4994FD1E0CF2";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:8]";
	setAttr ".ovs" no;
	setAttr ".ove" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 7 ".gtag";
	setAttr ".gtag[0].gtagnm" -type "string" "back";
	setAttr ".gtag[0].gtagcmp" -type "componentList" 1 "f[3]";
	setAttr ".gtag[1].gtagnm" -type "string" "bottom";
	setAttr ".gtag[1].gtagcmp" -type "componentList" 1 "f[4]";
	setAttr ".gtag[2].gtagnm" -type "string" "front";
	setAttr ".gtag[2].gtagcmp" -type "componentList" 1 "f[1]";
	setAttr ".gtag[3].gtagnm" -type "string" "left";
	setAttr ".gtag[3].gtagcmp" -type "componentList" 1 "f[6]";
	setAttr ".gtag[4].gtagnm" -type "string" "right";
	setAttr ".gtag[4].gtagcmp" -type "componentList" 1 "f[5]";
	setAttr ".gtag[5].gtagnm" -type "string" "rim";
	setAttr ".gtag[5].gtagcmp" -type "componentList" 2 "e[0:3]" "e[16:23]";
	setAttr ".gtag[6].gtagnm" -type "string" "top";
	setAttr ".gtag[6].gtagcmp" -type "componentList" 1 "f[2]";
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 26 ".uvst[0].uvsp[0:25]" -type "float2" 0 0 1 0 1 1 0 1 0.375
		 0 0.625 0 0.625 0.25 0.375 0.25 0.625 0.5 0.375 0.5 0.625 0.75 0.375 0.75 0.625 1
		 0.375 1 0.875 0 0.875 0.25 0.125 0 0.125 0.25 0 0 1 0 1 1 0 1 0 0 1 0 1 1 0 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 20 ".vt[0:19]"  -6.6613381e-16 0 -1.5 6.6613381e-16 0 1.5
		 -6.6613381e-16 0 -1.5 6.6613381e-16 0 1.5 -1 -1 1 1 -1 1 -1 1 1 1 1 1 -1 1 -1 1 1 -1
		 -1 -1 -1 1 -1 -1 6.6613381e-16 1.5 0 -6.6613381e-16 -1.5 0 6.6613381e-16 1.5 0 -6.6613381e-16 -1.5 0
		 -1.5 0 0 1.5 0 0 -1.5 0 0 1.5 0 0;
	setAttr -s 24 ".ed[0:23]"  0 1 0 0 2 0 1 3 0 2 3 0 4 5 0 6 7 0 8 9 0
		 10 11 0 4 6 0 5 7 0 6 8 0 7 9 0 8 10 0 9 11 0 10 4 0 11 5 0 12 13 0 12 14 0 13 15 0
		 14 15 0 16 17 0 16 18 0 17 19 0 18 19 0;
	setAttr -s 9 -ch 36 ".fc[0:8]" -type "polyFaces" 
		f 4 0 2 -4 -2
		mu 0 4 0 1 2 3
		f 4 4 9 -6 -9
		mu 0 4 4 5 6 7
		f 4 5 11 -7 -11
		mu 0 4 7 6 8 9
		f 4 6 13 -8 -13
		mu 0 4 9 8 10 11
		f 4 7 15 -5 -15
		mu 0 4 11 10 12 13
		f 4 -16 -14 -12 -10
		mu 0 4 5 14 15 6
		f 4 14 8 10 12
		mu 0 4 16 4 7 17
		f 4 16 18 -20 -18
		mu 0 4 18 19 20 21
		f 4 20 22 -24 -22
		mu 0 4 22 23 24 25;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode groupId -n "groupId16";
	rename -uid "48CF0C15-4D5A-AB8A-7C71-D0B021DEB9F9";
	setAttr ".ihi" 0;
createNode groupId -n "groupId15";
	rename -uid "A20B601C-4380-0BAC-2F11-18A33731BEF3";
	setAttr ".ihi" 0;
select -ne :time1;
	setAttr ".o" 0;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
	setAttr ".rtfm" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "groupId16.id" "controlGroup_controlShape.iog.og[0].gid";
connectAttr ":initialShadingGroup.mwc" "controlGroup_controlShape.iog.og[0].gco"
		;
connectAttr "groupId15.id" "controlGroup_controlShape.ciog.cog[0].cgid";
connectAttr "controlGroup_controlShape.ciog.cog[0]" ":initialShadingGroup.dsm" -na
		;
connectAttr "controlGroup_controlShape.iog.og[0]" ":initialShadingGroup.dsm" -na
		;
connectAttr "groupId16.msg" ":initialShadingGroup.gn" -na;
// End of controlGroup_control.ma
