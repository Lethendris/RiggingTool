//Maya ASCII 2025ff03 scene
//Name: hierarchy_representation.ma
//Last modified: Fri, Jun 13, 2025 12:31:46 AM
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
fileInfo "UUID" "9185EE12-4A81-C6BD-93EE-0F922B79A7C8";
createNode transform -s -n "persp";
	rename -uid "70A3106F-4EE0-A3EF-60A8-989D7E22E8AB";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 2.0069067944389616 0.85027264948791548 4.2881402310957926 ;
	setAttr ".r" -type "double3" -17.73835272960283 8.1999999999999904 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "DAF43A62-48C9-2DCC-B3E8-A8A1A6E0F971";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 4.5062792136728804;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0.49999996034560179 -3.6215870302669373e-08 3.6215870080624768e-08 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "BB0F30AE-42F8-3861-6260-5AAE9421B8A1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "12ABCA35-44AC-4D8C-0F48-66B62B21B2B8";
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
	rename -uid "2D384611-4092-9616-231A-9E91F5D34AFC";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "6ED47C39-4B81-8502-C972-AFBB9AFC6ABB";
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
	rename -uid "CCA9703E-407C-28C0-E0FE-FBB42321BC53";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "E2B463CD-4F96-9CE5-E613-CC8D3A79FD7F";
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
createNode transform -n "hierarchy_representation";
	rename -uid "3828A2FD-4252-5A80-2482-6FAFE1176D9D";
	setAttr ".rp" -type "double3" 0 -3.6198747094300576e-18 0 ;
	setAttr ".sp" -type "double3" 0 -3.6198747094300576e-18 0 ;
createNode nurbsSurface -n "hierarchy_representationShape" -p "hierarchy_representation";
	rename -uid "BE1E304F-43DD-9252-3AAD-A5BB42E0F7E8";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".cc" -type "nurbsSurface" 
		3 3 0 2 no 
		6 0 0 0 1 1 1
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		
		44
		-1.2459487396707148e-17 -0.15305627139851885 -0.15305627139852029
		-9.6124998990829383e-17 -0.21645425481804426 5.4021712373269767e-18
		-6.7970638627964975e-17 -0.15305627139851885 0.15305627139852052
		-1.1102230246251544e-16 4.7521545165801788e-16 0.21645425481805436
		6.7970638627965665e-17 0.1530562713985204 0.15305627139852052
		9.6124998990829925e-17 0.21645425481804548 4.0338542498532198e-17
		1.2348178985922344e-16 0.15305627139852029 -0.15305627139852029
		5.5511151231258061e-17 5.1595426875508071e-16 -0.21645425481805436
		-1.2459487396707148e-17 -0.15305627139851885 -0.15305627139852029
		-9.6124998990829383e-17 -0.21645425481804426 5.4021712373269767e-18
		-6.7970638627964975e-17 -0.15305627139851885 0.15305627139852052
		0.33333333333333331 -0.15305627139851899 -0.15305627139851918
		0.33333333333333326 -0.21645425481804439 -7.035276598382521e-18
		0.3333333333333332 -0.15305627139851899 0.15305627139851918
		0.33333333333333326 3.2718571504133028e-16 0.21645425481805436
		0.33333333333333331 0.15305627139852027 0.15305627139851918
		0.33333333333333348 0.21645425481804534 2.7901094662822503e-17
		0.33333333333333343 0.15305627139852016 -0.15305627139851918
		0.33333333333333337 3.6792453213839316e-16 -0.21645425481805436
		0.33333333333333331 -0.15305627139851899 -0.15305627139851918
		0.33333333333333326 -0.21645425481804439 -7.035276598382521e-18
		0.3333333333333332 -0.15305627139851899 0.15305627139851918
		0.66666666666666663 -0.15305627139851916 -0.15305627139851918
		0.66666666666666652 -0.21645425481804456 -1.9472724434092179e-17
		0.66666666666666652 -0.15305627139851916 0.15305627139851918
		0.66666666666666663 1.7915597842464262e-16 0.21645425481805436
		0.66666666666666674 0.1530562713985201 0.15305627139851918
		0.66666666666666674 0.21645425481804517 1.546364682711234e-17
		0.66666666666666685 0.15305627139851999 -0.15305627139851918
		0.66666666666666674 2.198947955217056e-16 -0.21645425481805436
		0.66666666666666663 -0.15305627139851916 -0.15305627139851918
		0.66666666666666652 -0.21645425481804456 -1.9472724434092179e-17
		0.66666666666666652 -0.15305627139851916 0.15305627139851918
		0.99999999999999989 -0.15305627139851929 -0.15305627139852052
		0.99999999999999989 -0.2164542548180447 -3.1910172269802459e-17
		0.99999999999999989 -0.15305627139851929 0.15305627139852029
		1 3.1126241807955166e-17 0.21645425481805436
		1 0.15305627139851996 0.15305627139852029
		1 0.21645425481804503 3.0261989914019052e-18
		1 0.15305627139851985 -0.15305627139852052
		1 7.1865058905018095e-17 -0.21645425481805436
		0.99999999999999989 -0.15305627139851929 -0.15305627139852052
		0.99999999999999989 -0.2164542548180447 -3.1910172269802459e-17
		0.99999999999999989 -0.15305627139851929 0.15305627139852029
		
		;
createNode transform -n "hierarchy_arrow_representation" -p "hierarchy_representation";
	rename -uid "45985476-4FF1-9BCD-4052-F1894C30C8CA";
	addAttr -is true -ci true -k true -sn "currentUVSet" -ln "currentUVSet" -dt "string";
	setAttr -k on ".currentUVSet" -type "string" "map1";
createNode mesh -n "hierarchy_arrow_representationShape" -p "hierarchy_arrow_representation";
	rename -uid "686CBE06-4598-DDF7-E845-6092070CDB9A";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 9 ".uvst[0].uvsp[0:8]" -type "float2" 0.61048543 0.73326457
		 0.5 0.6875 0.38951457 0.73326457 0.34375 0.84375 0.38951457 0.95423543 0.5 1 0.61048543
		 0.95423543 0.65625 0.84375 0.5 0.84375;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 9 ".pt[0:8]" -type "float3"  -0.41655758 -1.1165004 0.31380457 
		0.38315114 -0.63059616 0.44378656 1.1828599 -0.14469196 0.31380454 1.51411 0.056576073 
		0 1.1828599 -0.14469196 -0.31380454 0.38315123 -0.63059628 -0.44378662 -0.41655758 
		-1.1165004 -0.31380457 -0.74780774 -1.3177685 4.2300075e-09 0.61684877 -1.0152193 
		0;
	setAttr -s 9 ".vt[0:8]"  0.79970872 0.63059616 -0.79970884 -2.8004098e-16 0.63059616 -1.1309588
		 -0.79970872 0.63059616 -0.79970872 -1.1309588 0.63059616 0 -0.79970872 0.63059616 0.79970872
		 -2.8004098e-16 0.63059628 1.13095891 0.79970872 0.63059616 0.79970884 1.13095891 0.63059616 -1.0779876e-08
		 0 1.015219331 0;
	setAttr -s 16 ".ed[0:15]"  0 1 0 1 8 0 8 0 0 1 2 0 2 8 0 2 3 0 3 8 0
		 3 4 0 4 8 0 4 5 0 5 8 0 5 6 0 6 8 0 6 7 0 7 8 0 7 0 0;
	setAttr -s 32 ".n[0:31]" -type "float3"  1.55817246 -0.37470469 -0.37470463
		 1.5581727 4.2784368e-08 -0.52991247 1.64581561 2.7427424e-08 -5.4854848e-08 1.5581727
		 4.2784368e-08 -0.52991247 1.55817246 0.37470469 -0.37470463 1.64581561 2.7427424e-08
		 -5.4854848e-08 1.55817246 0.37470469 -0.37470463 1.55817246 0.52991247 0 1.64581561
		 2.7427424e-08 -5.4854848e-08 1.55817246 0.52991247 0 1.55817246 0.37470481 0.37470457
		 1.64581561 2.7427424e-08 -5.4854848e-08 1.55817246 0.37470481 0.37470457 1.5581727
		 5.3480466e-08 0.52991229 1.64581561 2.7427424e-08 -5.4854848e-08 1.5581727 5.3480466e-08
		 0.52991229 1.55817246 -0.37470478 0.37470454 1.64581561 2.7427424e-08 -5.4854848e-08
		 1.55817246 -0.37470478 0.37470454 1.5581727 -0.52991247 0 1.64581561 2.7427424e-08
		 -5.4854848e-08 1.5581727 -0.52991247 0 1.55817246 -0.37470469 -0.37470463 1.64581561
		 2.7427424e-08 -5.4854848e-08 -1.64581561 3.9633459e-15 2.7115814e-08 -1.64581549
		 3.9633459e-15 2.7115814e-08 -1.64581561 3.9633459e-15 2.7115814e-08 -1.64581549 3.9633459e-15
		 2.7115814e-08 -1.64581561 3.9633459e-15 2.7115814e-08 -1.64581549 3.9633459e-15 2.7115814e-08
		 -1.64581561 3.9633459e-15 2.7115814e-08 -1.64581549 3.9633459e-15 2.7115814e-08;
	setAttr -s 9 -ch 32 ".fc[0:8]" -type "polyFaces" 
		f 3 0 1 2
		mu 0 3 6 5 8
		f 3 3 4 -2
		mu 0 3 5 4 8
		f 3 5 6 -5
		mu 0 3 4 3 8
		f 3 7 8 -7
		mu 0 3 3 2 8
		f 3 9 10 -9
		mu 0 3 2 1 8
		f 3 11 12 -11
		mu 0 3 1 0 8
		f 3 13 14 -13
		mu 0 3 0 7 8
		f 3 15 -3 -15
		mu 0 3 7 6 8
		f 8 -1 -16 -14 -12 -10 -8 -6 -4
		mu 0 8 5 6 7 0 1 2 3 4;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "06A1C841-4CD8-7B3C-1B0E-59B1AD7506C3";
	setAttr -s 4 ".lnk";
	setAttr -s 4 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "289DAE60-4F4C-7F2A-2F16-FAB92D36D2F7";
createNode displayLayer -n "defaultLayer";
	rename -uid "5315CA94-48B0-0F1D-68D9-C9AAFE691C1B";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "5C79ADB4-40D8-BB8C-3957-EC809670A3BF";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "22F84387-4831-45B9-F6E0-9FB494549534";
	setAttr ".g" yes;
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "3E60CDFB-4E69-00DF-4699-4F9B0EE60030";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "4AB90288-4EA4-6E2E-D5C0-3A9080ADFB97";
createNode standardSurface -n "standardSurface2";
	rename -uid "9E738E8E-45C7-BAA5-E459-44BFE9153713";
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
createNode shadingEngine -n "hierarchy_representationSG";
	rename -uid "430F7C63-48A8-8652-F204-4C9866FD288E";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "6E782EE2-4909-5E66-5DEC-42864B835982";
createNode shadingEngine -n "hierarchy_arrow_representationSG";
	rename -uid "9157E312-449B-EB38-D249-4B863D5AFE95";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
	rename -uid "DF29B908-403C-A4AF-8A43-A59163A64589";
createNode aiOptions -s -n "defaultArnoldRenderOptions";
	rename -uid "3D62A069-48F1-1676-A1D3-78AFE0FC0943";
	setAttr ".version" -type "string" "5.4.2.1";
createNode aiAOVFilter -s -n "defaultArnoldFilter";
	rename -uid "BD67EC29-488B-1A88-8D97-BAA50FD9D0B6";
	setAttr ".ai_translator" -type "string" "gaussian";
createNode aiAOVDriver -s -n "defaultArnoldDriver";
	rename -uid "48AC6757-4EA0-D1DB-FB87-A79C4737A074";
	setAttr ".ai_translator" -type "string" "exr";
createNode aiAOVDriver -s -n "defaultArnoldDisplayDriver";
	rename -uid "97A3649B-4132-5984-EFCA-BC9E22E1F044";
	setAttr ".ai_translator" -type "string" "maya";
	setAttr ".output_mode" 0;
createNode aiImagerDenoiserOidn -s -n "defaultArnoldDenoiser";
	rename -uid "645898D6-4116-6AD6-1E45-298F5F334E6A";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "D2205839-4CB8-CC9F-A5EC-E69FECE5E8C3";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 24 -ast 0 -aet 48 ";
	setAttr ".st" 6;
createNode container -n "hierarchy_representation_container";
	rename -uid "0B966800-498D-4740-486D-46823E1F1729";
	setAttr ".isc" yes;
	setAttr ".ctor" -type "string" "Hakan";
	setAttr ".cdat" -type "string" "2025/06/13 00:31:35";
createNode hyperLayout -n "hyperLayout1";
	rename -uid "B8EDEC62-4072-271A-1441-FDA06F6EB538";
	setAttr ".ihi" 0;
	setAttr -s 2 ".hyp";
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "CF1A9B5E-49B2-1B30-C494-6ABBE11B71EC";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" 0.59523807158545394 -18.452380219149241 ;
	setAttr ".tgi[0].vh" -type "double2" 114.88094781599366 12.499999503294648 ;
	setAttr -s 7 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" -192.85714721679688;
	setAttr ".tgi[0].ni[0].y" 182.85714721679688;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" -192.85714721679688;
	setAttr ".tgi[0].ni[1].y" -20;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" -192.85714721679688;
	setAttr ".tgi[0].ni[2].y" 81.428573608398438;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" -192.85714721679688;
	setAttr ".tgi[0].ni[3].y" -121.42857360839844;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 114.28571319580078;
	setAttr ".tgi[0].ni[4].y" 31.428571701049805;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" -34.285713195800781;
	setAttr ".tgi[0].ni[5].y" 30;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" -195.71427917480469;
	setAttr ".tgi[0].ni[6].y" 30;
	setAttr ".tgi[0].ni[6].nvs" 18304;
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
	setAttr -s 6 ".s";
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
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "hierarchy_representationSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "hierarchy_arrow_representationSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "hierarchy_representationSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "hierarchy_arrow_representationSG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "standardSurface2.oc" "hierarchy_representationSG.ss";
connectAttr "hierarchy_representationShape.iog" "hierarchy_representationSG.dsm"
		 -na;
connectAttr "hierarchy_representationSG.msg" "materialInfo1.sg";
connectAttr "standardSurface2.msg" "materialInfo1.m";
connectAttr "standardSurface2.oc" "hierarchy_arrow_representationSG.ss";
connectAttr "hierarchy_arrow_representationShape.iog" "hierarchy_arrow_representationSG.dsm"
		 -na;
connectAttr "hierarchy_arrow_representationSG.msg" "materialInfo2.sg";
connectAttr "standardSurface2.msg" "materialInfo2.m";
connectAttr ":defaultArnoldDenoiser.msg" ":defaultArnoldRenderOptions.imagers" -na
		;
connectAttr ":defaultArnoldDisplayDriver.msg" ":defaultArnoldRenderOptions.drivers"
		 -na;
connectAttr ":defaultArnoldFilter.msg" ":defaultArnoldRenderOptions.filt";
connectAttr ":defaultArnoldDriver.msg" ":defaultArnoldRenderOptions.drvr";
connectAttr "hyperLayout1.msg" "hierarchy_representation_container.hl";
connectAttr "hierarchy_representation.msg" "hyperLayout1.hyp[0].dn";
connectAttr "hierarchy_representationShape.msg" "hyperLayout1.hyp[1].dn";
connectAttr ":defaultArnoldDenoiser.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn"
		;
connectAttr ":defaultArnoldFilter.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn"
		;
connectAttr ":defaultArnoldDisplayDriver.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn"
		;
connectAttr ":defaultArnoldDriver.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn"
		;
connectAttr ":defaultArnoldRenderOptions.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "hierarchy_representation_container.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn"
		;
connectAttr "hyperLayout1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn";
connectAttr "hierarchy_representationSG.pa" ":renderPartition.st" -na;
connectAttr "hierarchy_arrow_representationSG.pa" ":renderPartition.st" -na;
connectAttr "standardSurface2.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of hierarchy_representation.ma
