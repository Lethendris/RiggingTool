//Maya ASCII 2025ff03 scene
//Name: translation_control.ma
//Last modified: Sun, Jun 08, 2025 02:02:25 AM
//Codeset: 1252
requires maya "2025ff03";
requires "mtoa" "5.4.2.1";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2025";
fileInfo "version" "2025";
fileInfo "cutIdentifier" "202407121012-8ed02f4c99";
fileInfo "osv" "Windows 11 Pro v2009 (Build: 26100)";
fileInfo "UUID" "3BD23159-4AF6-9DC2-E952-1B89FAB8B828";
createNode transform -s -n "persp";
	rename -uid "2A8E8160-4058-A3F0-EF30-67A39C7A1E1E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 4.7323728313697391 3.5492796235272799 4.7323728313697204 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "3CE9F265-4ABC-0438-AFB0-1D8F15C06B47";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 7.5754927942780377;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "293432BF-43F9-902C-563D-ADBB814924A5";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "66C8F645-4F6D-321B-771C-8FBB288F9FE3";
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
	rename -uid "1F11006A-4CBF-33B3-5020-D6A87B621F9D";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "8D4E98C3-4399-4B95-3B3F-B498063A8DAC";
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
	rename -uid "3A626377-4E10-2464-8D7F-73BBC385E134";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "8C7F40A3-46A4-9BA3-781D-EAB972561453";
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
createNode dagContainer -n "translation_control_container";
	rename -uid "850488EF-4DB5-90E2-6DFF-90972D55A159";
	setAttr ".isc" yes;
	setAttr ".ctor" -type "string" "Hakan";
	setAttr ".cdat" -type "string" "2025/06/08 02:02:11";
	setAttr ".rp" -type "double3" -3.3306690738754696e-16 0 0 ;
	setAttr ".sp" -type "double3" -3.3306690738754696e-16 0 0 ;
createNode transform -n "translation_control" -p "translation_control_container";
	rename -uid "A36481F3-4A7A-02AD-C349-F8A7930D13CE";
createNode nurbsSurface -n "translation_controlShape" -p "translation_control";
	rename -uid "2E0497A0-4699-A741-28F9-43AB6C05CA76";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".cc" -type "nurbsSurface" 
		3 3 0 2 no 
		9 0 0 0 1 2 3 4 4 4
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		
		77
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		9.5964746819769475e-17 -1 -2.5316183359690652e-16
		0.19991679083637276 -1 -0.19991679083637284
		0.28272503694690354 -1 -1.1177774761168466e-16
		0.19991679083637276 -1 0.19991679083637268
		4.7890007918352597e-17 -1 0.2827250369469036
		-0.19991679083637273 -1 0.19991679083637273
		-0.28272503694690371 -1 3.2191243563517383e-19
		-0.19991679083637276 -1 -0.19991679083637279
		-7.1788605542032352e-17 -1 -0.28272503694690371
		0.19991679083637276 -1 -0.19991679083637284
		0.28272503694690354 -1 -1.1177774761168466e-16
		0.19991679083637276 -1 0.19991679083637268
		0.61642997969058977 -0.78361162489122427 -0.61642997969058977
		0.87176363753180319 -0.78361162489122427 -4.7776033311964345e-17
		0.61642997969058966 -0.78361162489122427 0.61642997969058977
		-8.3940866021681387e-18 -0.78361162489122427 0.87176363753180353
		-0.61642997969058977 -0.78361162489122427 0.61642997969058977
		-0.87176363753180375 -0.78361162489122427 -1.4243681125611212e-17
		-0.61642997969058966 -0.78361162489122427 -0.61642997969058977
		-6.529563193606176e-17 -0.78361162489122427 -0.87176363753180353
		0.61642997969058977 -0.78361162489122427 -0.61642997969058977
		0.87176363753180319 -0.78361162489122427 -4.7776033311964345e-17
		0.61642997969058966 -0.78361162489122427 0.61642997969058977
		0.86720244749154218 1.7637621209264518e-16 -0.86720244749154185
		1.2264094625656801 1.2327537701598182e-16 7.5095921138754302e-17
		0.86720244749154174 7.0174541939318428e-17 0.86720244749154207
		-8.6614559170421727e-17 4.8179455877227502e-17 1.2264094625656805
		-0.86720244749154207 7.0174541939318453e-17 0.86720244749154185
		-1.2264094625656807 1.2327537701598182e-16 -2.7341567632466632e-17
		-0.86720244749154174 1.7637621209264521e-16 -0.86720244749154207
		-1.7053183114584738e-17 1.9837129815473613e-16 -1.2264094625656805
		0.86720244749154218 1.7637621209264518e-16 -0.86720244749154185
		1.2264094625656801 1.2327537701598182e-16 7.5095921138754302e-17
		0.86720244749154174 7.0174541939318428e-17 0.86720244749154207
		0.61642997969058988 0.78361162489122471 -0.61642997969058966
		0.87176363753180319 0.78361162489122471 1.5453628814360203e-16
		0.61642997969058955 0.78361162489122471 0.61642997969058988
		-1.147416612379651e-16 0.78361162489122471 0.87176363753180353
		-0.61642997969058988 0.78361162489122471 0.61642997969058966
		-0.87176363753180375 0.78361162489122471 -2.4626508941638749e-17
		-0.61642997969058955 0.78361162489122471 -0.61642997969058988
		4.105194269973521e-17 0.78361162489122471 -0.87176363753180353
		0.61642997969058988 0.78361162489122471 -0.61642997969058966
		0.87176363753180319 0.78361162489122471 1.5453628814360203e-16
		0.61642997969058955 0.78361162489122471 0.61642997969058988
		0.19991679083637259 1 -0.19991679083637234
		0.28272503694690315 1 1.4640157876526888e-16
		0.19991679083637237 1 0.19991679083637262
		-8.7824638543865684e-17 1 0.28272503694690332
		-0.19991679083637257 1 0.19991679083637245
		-0.28272503694690332 1 -1.2928054111847823e-17
		-0.19991679083637237 1 -0.19991679083637251
		6.3926040920185966e-17 1 -0.28272503694690321
		0.19991679083637259 1 -0.19991679083637234
		0.28272503694690315 1 1.4640157876526888e-16
		0.19991679083637237 1 0.19991679083637262
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		-8.6998366831816947e-17 1 2.4419545360895402e-16
		
		;
	setAttr ".nufa" 4.5;
	setAttr ".nvfa" 4.5;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "A80E3F9B-4096-CAFA-A24A-08966E5D473B";
	setAttr -s 3 ".lnk";
	setAttr -s 3 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "88677116-467F-EE04-0DD4-A8A00DDDB9B8";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "1B0B2A7B-40D4-AF0B-8F01-C58351FC62F8";
createNode displayLayerManager -n "layerManager";
	rename -uid "F4D61E37-46D6-BACC-E83D-EDAB661A6B30";
createNode displayLayer -n "defaultLayer";
	rename -uid "A2B1F0B9-4283-52FF-66F1-EBADD8962907";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "D0202266-4B45-0C1F-49F4-78B793A43AE5";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "E30AE97F-4F1B-021A-3026-D681B4519E89";
	setAttr ".g" yes;
createNode lambert -n "m_translation_control";
	rename -uid "C7B8F6C7-4A1E-EF5A-9F0B-DABC76794ED0";
	setAttr ".dc" 0.20000000298023224;
	setAttr ".c" -type "float3" 1 0 0 ;
createNode shadingEngine -n "lambert2SG";
	rename -uid "BA90F082-4E7E-F56E-4B75-EF943ECAF679";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "F8CA84FD-44F4-5775-AC2D-DE9C6A7F0CB5";
createNode hyperLayout -n "hyperLayout1";
	rename -uid "E317E818-4EEF-A5BF-DD1C-3EACBA511969";
	setAttr ".ihi" 0;
	setAttr -s 3 ".hyp";
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "D772EB1C-4988-411D-EFB2-63BB383104B4";
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
	setAttr -s 3 ".st";
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
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "hyperLayout1.msg" "translation_control_container.hl";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "m_translation_control.oc" "lambert2SG.ss";
connectAttr "translation_controlShape.iog" "lambert2SG.dsm" -na;
connectAttr "lambert2SG.msg" "materialInfo1.sg";
connectAttr "m_translation_control.msg" "materialInfo1.m";
connectAttr "m_translation_control.msg" "hyperLayout1.hyp[0].dn";
connectAttr "translation_controlShape.msg" "hyperLayout1.hyp[1].dn";
connectAttr "translation_control.msg" "hyperLayout1.hyp[2].dn";
connectAttr "lambert2SG.pa" ":renderPartition.st" -na;
connectAttr "m_translation_control.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of translation_control.ma
