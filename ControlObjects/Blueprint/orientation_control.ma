//Maya ASCII 2025ff03 scene
//Name: orientation_control.ma
//Last modified: Sat, Jun 14, 2025 10:30:18 AM
//Codeset: 1252
requires maya "2025ff03";
requires -nodeType "aiOptions" -nodeType "aiAOVDriver" -nodeType "aiAOVFilter" -nodeType "aiImagerDenoiserOidn"
		 "mtoa" "5.4.2.1";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2025";
fileInfo "version" "2025";
fileInfo "cutIdentifier" "202407121012-8ed02f4c99";
fileInfo "osv" "Windows 11 Pro v2009 (Build: 26100)";
fileInfo "UUID" "1E2F98B8-4A41-A61A-A07B-F2A9342C6518";
createNode transform -n "orientation_control";
	rename -uid "81451414-479B-AA16-1013-E0B45482A5BB";
createNode mesh -n "orientation_controlShape" -p "orientation_control";
	rename -uid "BE4E7A4A-40B7-0E5B-E909-D0A475A3E9B0";
	setAttr -k off ".v";
	setAttr -s 2 ".iog[0].og";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:14]";
	setAttr ".iog[0].og[1].gcl" -type "componentList" 1 "f[15:29]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 7 ".gtag";
	setAttr ".gtag[0].gtagnm" -type "string" "back";
	setAttr ".gtag[0].gtagcmp" -type "componentList" 2 "f[11]" "f[26]";
	setAttr ".gtag[1].gtagnm" -type "string" "bottom";
	setAttr ".gtag[1].gtagcmp" -type "componentList" 4 "f[0]" "f[12]" "f[15]" "f[27]";
	setAttr ".gtag[2].gtagnm" -type "string" "front";
	setAttr ".gtag[2].gtagcmp" -type "componentList" 2 "f[9]" "f[24]";
	setAttr ".gtag[3].gtagnm" -type "string" "left";
	setAttr ".gtag[3].gtagcmp" -type "componentList" 2 "f[14]" "f[29]";
	setAttr ".gtag[4].gtagnm" -type "string" "right";
	setAttr ".gtag[4].gtagcmp" -type "componentList" 2 "f[13]" "f[28]";
	setAttr ".gtag[5].gtagnm" -type "string" "sides";
	setAttr ".gtag[5].gtagcmp" -type "componentList" 2 "f[1:8]" "f[16:23]";
	setAttr ".gtag[6].gtagnm" -type "string" "top";
	setAttr ".gtag[6].gtagcmp" -type "componentList" 2 "f[10]" "f[25]";
	setAttr ".pv" -type "double2" 0.5 1 ;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 64 ".uvst[0].uvsp[0:63]" -type "float2" 0.67677665 0.073223323
		 0.5 2.9802322e-08 0.32322332 0.073223323 0.25000003 0.25 0.32322332 0.42677668 0.5
		 0.5 0.67677671 0.42677671 0.75 0.25 0.25 0.5 0.3125 0.5 0.375 0.5 0.4375 0.5 0.5
		 0.5 0.5625 0.5 0.625 0.5 0.6875 0.5 0.75 0.5 0.5 1 0.375 0.25 0.375 0 0.625 0 0.625
		 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.625 1 0.375 1 0.875 0 0.875 0.25
		 0.125 0 0.125 0.25 0.67677665 0.073223323 0.75 0.25 0.67677671 0.42677671 0.5 0.5
		 0.32322332 0.42677668 0.25000003 0.25 0.32322332 0.073223323 0.5 2.9802322e-08 0.25
		 0.5 0.3125 0.5 0.5 1 0.375 0.5 0.4375 0.5 0.5 0.5 0.5625 0.5 0.625 0.5 0.6875 0.5
		 0.75 0.5 0.375 0.25 0.375 0 0.625 0 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625
		 0.75 0.625 1 0.375 1 0.875 0 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 18 ".pt";
	setAttr ".pt[0]" -type "float3" 0.053032994 0 0 ;
	setAttr ".pt[2]" -type "float3" -0.053032994 0 0 ;
	setAttr ".pt[3]" -type "float3" -0.074999988 0 0 ;
	setAttr ".pt[4]" -type "float3" -0.053032994 0 0 ;
	setAttr ".pt[6]" -type "float3" 0.053032994 0 0 ;
	setAttr ".pt[7]" -type "float3" 0.074999988 0 0 ;
	setAttr ".pt[8]" -type "float3" 0 0 0.1 ;
	setAttr ".pt[17]" -type "float3" 0.053033002 -1.1175871e-08 -7.4505806e-09 ;
	setAttr ".pt[18]" -type "float3" 0 -1.1175871e-08 -2.2351742e-08 ;
	setAttr ".pt[19]" -type "float3" -0.053033005 -1.1175871e-08 -7.4505806e-09 ;
	setAttr ".pt[20]" -type "float3" -0.07500004 -1.1175871e-08 0 ;
	setAttr ".pt[21]" -type "float3" -0.053033005 -1.1175871e-08 7.4505806e-09 ;
	setAttr ".pt[22]" -type "float3" 0 -1.1175871e-08 2.2351742e-08 ;
	setAttr ".pt[23]" -type "float3" 0.053033002 -1.1175871e-08 3.7252903e-09 ;
	setAttr ".pt[24]" -type "float3" 0.07500001 -1.1175871e-08 0 ;
	setAttr ".pt[25]" -type "float3" 0 0.10000003 0 ;
	setAttr -s 34 ".vt[0:33]"  0.55303299 0.053033005 0.5 0.5 0.074999996 0.5
		 0.44696701 0.053033005 0.5 0.42500001 -2.220446e-16 0.5 0.44696701 -0.053033005 0.5
		 0.5 -0.074999996 0.5 0.55303299 -0.053033009 0.5 0.57499999 -2.220446e-16 0.5 0.5 -2.8865798e-16 0.64999998
		 0 -0.075000003 -0.5 1 -0.075000003 -0.5 0 -0.075000003 0.5 1 -0.075000003 0.5 0 0.075000003 0.5
		 1 0.075000003 0.5 0 0.075000003 -0.5 1 0.075000003 -0.5 0.55303299 0.5 -0.053033005
		 0.5 0.5 -0.074999996 0.44696701 0.5 -0.053033005 0.42500001 0.5 0 0.44696701 0.5 0.053033005
		 0.5 0.5 0.074999996 0.55303299 0.5 0.053033009 0.57499999 0.5 0 0.5 0.64999998 0
		 0 -0.5 0.075000003 1 -0.5 0.075000003 0 0.5 0.075000003 1 0.5 0.075000003 0 0.5 -0.075000003
		 1 0.5 -0.075000003 0 -0.5 -0.075000003 1 -0.5 -0.075000003;
	setAttr -s 56 ".ed[0:55]"  0 1 0 1 2 0 2 3 0 3 4 0 4 5 0 5 6 0 6 7 0
		 7 0 0 0 8 0 1 8 0 2 8 0 3 8 0 4 8 0 5 8 0 6 8 0 7 8 0 9 10 0 9 11 0 10 12 0 11 13 0
		 12 14 0 13 15 0 14 16 0 15 9 0 16 10 0 11 12 0 13 14 0 15 16 0 17 18 0 18 19 0 19 20 0
		 20 21 0 21 22 0 22 23 0 23 24 0 24 17 0 17 25 0 18 25 0 19 25 0 20 25 0 21 25 0 22 25 0
		 23 25 0 24 25 0 26 27 0 26 28 0 27 29 0 28 30 0 29 31 0 30 32 0 31 33 0 32 26 0 33 27 0
		 28 29 0 30 31 0 32 33 0;
	setAttr -s 30 -ch 112 ".fc[0:29]" -type "polyFaces" 
		f 8 -8 -7 -6 -5 -4 -3 -2 -1
		mu 0 8 0 7 6 5 4 3 2 1
		f 3 0 9 -9
		mu 0 3 8 9 17
		f 3 1 10 -10
		mu 0 3 9 10 17
		f 3 2 11 -11
		mu 0 3 10 11 17
		f 3 3 12 -12
		mu 0 3 11 12 17
		f 3 4 13 -13
		mu 0 3 12 13 17
		f 3 5 14 -14
		mu 0 3 13 14 17
		f 3 6 15 -15
		mu 0 3 14 15 17
		f 3 7 8 -16
		mu 0 3 15 16 17
		f 4 -18 16 18 -26
		mu 0 4 18 19 20 21
		f 4 -20 25 20 -27
		mu 0 4 22 18 21 23
		f 4 -22 26 22 -28
		mu 0 4 24 22 23 25
		f 4 -17 -24 27 24
		mu 0 4 26 27 24 25
		f 4 -25 -23 -21 -19
		mu 0 4 20 28 29 21
		f 4 23 17 19 21
		mu 0 4 30 19 18 31
		f 8 -36 -35 -34 -33 -32 -31 -30 -29
		mu 0 8 32 33 34 35 36 37 38 39
		f 3 28 37 -37
		mu 0 3 40 41 42
		f 3 29 38 -38
		mu 0 3 41 43 42
		f 3 30 39 -39
		mu 0 3 43 44 42
		f 3 31 40 -40
		mu 0 3 44 45 42
		f 3 32 41 -41
		mu 0 3 45 46 42
		f 3 33 42 -42
		mu 0 3 46 47 42
		f 3 34 43 -43
		mu 0 3 47 48 42
		f 3 35 36 -44
		mu 0 3 48 49 42
		f 4 -46 44 46 -54
		mu 0 4 50 51 52 53
		f 4 -48 53 48 -55
		mu 0 4 54 50 53 55
		f 4 -50 54 50 -56
		mu 0 4 56 54 55 57
		f 4 -45 -52 55 52
		mu 0 4 58 59 56 57
		f 4 -53 -51 -49 -47
		mu 0 4 52 60 61 53
		f 4 51 45 47 49
		mu 0 4 62 51 50 63;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -s -n "persp";
	rename -uid "D866F36F-4890-56BC-0E08-66ACF070885A";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0.79762971320824516 1.3182035915760686 1.5771297990173878 ;
	setAttr ".r" -type "double3" -38.738352729605971 8.6000000000002093 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "B608CB4A-4318-5054-6996-A9848E8C65C0";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 1.7466624049247959;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0.5 0.074999988079071045 0.074999988079071045 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "0ED8BDCF-4D37-E4C8-7FE0-0FBD65086AFB";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "8AF64193-417D-C868-E7B0-15940BDA7221";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "front";
	rename -uid "AD58449B-4777-E70E-72D5-85BD89DE6134";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "8C6F14B6-4BA8-5335-6266-1A9FA0DCA29D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "side";
	rename -uid "C62D105E-4B17-E186-B00D-4A87EB7A25B3";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "326F0927-4D5B-B2C8-082F-9CADFEF4DA44";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode groupId -n "groupId12";
	rename -uid "644F8889-4965-3CA0-5075-F685DC656D87";
	setAttr ".ihi" 0;
createNode shadingEngine -n "lambert3SG";
	rename -uid "9C0D5A8B-4639-97FB-6175-3FA74B2EDA0A";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
	rename -uid "D4C1CD73-44B3-26D3-F3F7-79828B332DBD";
createNode lambert -n "m_orientation_control_zAxis";
	rename -uid "FA5A258C-46B2-BD62-0D80-4DA6392C1C72";
	setAttr ".dc" 0.20000000298023224;
	setAttr ".c" -type "float3" 0 0 1 ;
createNode groupId -n "groupId13";
	rename -uid "8AED6B7B-42A5-DEBA-79C7-F386A72D5599";
	setAttr ".ihi" 0;
createNode shadingEngine -n "lambert2SG";
	rename -uid "B7584ED6-47F5-DFE1-D478-DBB0F312650A";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "E4895779-412C-7BDC-A245-EB955A78B0C6";
createNode lambert -n "m_orientation_control_yAxis";
	rename -uid "5EB10BE5-47B7-7432-29FC-2DAC41BE3CA5";
	setAttr ".dc" 0.20000000298023224;
	setAttr ".c" -type "float3" 0 1 0 ;
createNode groupId -n "groupId11";
	rename -uid "A73A468F-4ADC-DEF2-AB18-2AB3B07484D3";
	setAttr ".ihi" 0;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "219DE3A8-4379-D835-2F5B-C09C4DC2BD41";
	setAttr -s 4 ".lnk";
	setAttr -s 4 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "408609A3-4935-3175-BC12-10A7E0F770E0";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "8F5FF7F5-4383-0836-90A7-79851D1D559D";
createNode displayLayerManager -n "layerManager";
	rename -uid "95C2D05C-4335-57E7-88E7-C79F30E3781B";
createNode displayLayer -n "defaultLayer";
	rename -uid "E23DD98E-49C6-CB33-AE75-7A8784DD6168";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "0B1FD1CE-44CE-F9CF-C2B1-68ADEB21C7B2";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "D01CD423-4618-C412-3A89-0A8F6C1D278E";
	setAttr ".g" yes;
createNode aiOptions -s -n "defaultArnoldRenderOptions";
	rename -uid "8B19BC38-4349-A101-BEEC-C1887A9EBE8D";
	setAttr ".version" -type "string" "5.4.2.1";
createNode aiAOVFilter -s -n "defaultArnoldFilter";
	rename -uid "51268AD7-4C43-C0B2-0DFC-40856C092229";
	setAttr ".ai_translator" -type "string" "gaussian";
createNode aiAOVDriver -s -n "defaultArnoldDriver";
	rename -uid "9A8291CA-44D6-C425-79D8-789BFC013415";
	setAttr ".ai_translator" -type "string" "exr";
createNode aiAOVDriver -s -n "defaultArnoldDisplayDriver";
	rename -uid "CEF33D15-4839-F4E6-721D-7BA26AC0BCB5";
	setAttr ".ai_translator" -type "string" "maya";
	setAttr ".output_mode" 0;
createNode aiImagerDenoiserOidn -s -n "defaultArnoldDenoiser";
	rename -uid "67D992D5-4B87-EBB7-351A-59A120B330D3";
createNode container -n "orientation_control_container";
	rename -uid "29697CD5-4A8D-F65F-5AF3-219B3F9F64B8";
	setAttr ".isc" yes;
	setAttr ".ctor" -type "string" "Hakan";
	setAttr ".cdat" -type "string" "2025/06/14 10:28:37";
createNode hyperLayout -n "hyperLayout1";
	rename -uid "31FAC68C-4D02-B071-19AD-6C9B2EB33521";
	setAttr ".ihi" 0;
	setAttr -s 4 ".hyp";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "B3E5EA52-4CA7-9A27-5537-8294E3B30512";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 24 -ast 0 -aet 48 ";
	setAttr ".st" 6;
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
	setAttr -s 4 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 7 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".dss" -type "string" "standardSurface1";
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
connectAttr "groupId12.id" "orientation_controlShape.iog.og[0].gid";
connectAttr "lambert3SG.mwc" "orientation_controlShape.iog.og[0].gco";
connectAttr "groupId13.id" "orientation_controlShape.iog.og[1].gid";
connectAttr "lambert2SG.mwc" "orientation_controlShape.iog.og[1].gco";
connectAttr "groupId11.id" "orientation_controlShape.ciog.cog[0].cgid";
connectAttr "m_orientation_control_zAxis.oc" "lambert3SG.ss";
connectAttr "orientation_controlShape.iog.og[0]" "lambert3SG.dsm" -na;
connectAttr "groupId12.msg" "lambert3SG.gn" -na;
connectAttr "lambert3SG.msg" "materialInfo2.sg";
connectAttr "m_orientation_control_zAxis.msg" "materialInfo2.m";
connectAttr "m_orientation_control_yAxis.oc" "lambert2SG.ss";
connectAttr "groupId13.msg" "lambert2SG.gn" -na;
connectAttr "orientation_controlShape.iog.og[1]" "lambert2SG.dsm" -na;
connectAttr "lambert2SG.msg" "materialInfo1.sg";
connectAttr "m_orientation_control_yAxis.msg" "materialInfo1.m";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert3SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert3SG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr ":defaultArnoldDenoiser.msg" ":defaultArnoldRenderOptions.imagers" -na
		;
connectAttr ":defaultArnoldDisplayDriver.msg" ":defaultArnoldRenderOptions.drivers"
		 -na;
connectAttr ":defaultArnoldFilter.msg" ":defaultArnoldRenderOptions.filt";
connectAttr ":defaultArnoldDriver.msg" ":defaultArnoldRenderOptions.drvr";
connectAttr "hyperLayout1.msg" "orientation_control_container.hl";
connectAttr "orientation_control.msg" "hyperLayout1.hyp[0].dn";
connectAttr "m_orientation_control_yAxis.msg" "hyperLayout1.hyp[1].dn";
connectAttr "m_orientation_control_zAxis.msg" "hyperLayout1.hyp[2].dn";
connectAttr "orientation_controlShape.msg" "hyperLayout1.hyp[3].dn";
connectAttr "lambert2SG.pa" ":renderPartition.st" -na;
connectAttr "lambert3SG.pa" ":renderPartition.st" -na;
connectAttr "m_orientation_control_yAxis.msg" ":defaultShaderList1.s" -na;
connectAttr "m_orientation_control_zAxis.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "orientation_controlShape.ciog.cog[0]" ":initialShadingGroup.dsm" -na
		;
// End of orientation_control.ma
