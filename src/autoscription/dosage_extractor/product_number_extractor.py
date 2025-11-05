"""0 is the return value of not fitting the rules."""
from __future__ import annotations

import re
from collections.abc import Callable
from copy import deepcopy
from typing import Optional

from src.autoscription.idika_client.model.mt.clinical_document.substance_administration import (
    SubstanceAdministration,
)

NO_NEED_TO_IDENTIFY = 0
KEY_ERROR = 9223372036854775806
UNABLE_TO_IDENTIFY = 9223372036854775807

product_list = {
    "SALMENT INH.SUS.P 25MCG/DOSE  BT X 1": 120,
    "TRELEGY ELLIPTA INH.PD.DOS MCG/DOSE BTX 1 ΣYΣKEYH  EIΣΠNOΩN": 30,
    # Pulmoton eg has 30, 60 and 120. We have dropped whatever is in the parenthesis where it is stated.
    # We select the max in order to be sure that no more have been given.
    "PULMOTON INH.PD.DOS MCG/DOSE BTX1": 120,
    "AVAMYS NASPR.SUS 27,5MC/ΨEKAΣMO 1 ΦIAΛH ΣE ΠΛAΣTIKH": 120,
    "PRICEFIL PD.ORA.SUS 250MG/5ML BTX1  FLX100 ML": 100,
    "PRICEFIL PD.ORA.SUS 250MG/5ML BTX1": 60,
    "SPIOLTO RESPIMAT SOL.INH MCG/EIΣΠNOH BT X 1 CARTRIDGE": 60,
    "SPIOLTO RESPIMAT SOL.INH MCG/EIΣΠNOH BT X 1 RESPIMAT  REUSABLE INHALER + 1 CARTRIDGE": 60,
    "SPIRIVA RESPIMAT SOL.INH 2,5MCG/PUFF BTX 1 RESPIMAT REUSABLE  INHALER +1 CARTRIDGE": 60,
    "SPIRIVA RESPIMAT SOL.INH 2,5MCG/PUFF BTX 1 CARTRIDGE": 60,
    "ONBREZ BREEZHALER  INHPD.CAP  0.300MG": 30,
    "AURID NASPR.SUS 100MCG/DOSE FLX10ML": 200,
    "AURID NASPR.SUS 50MCG/DOSE FLX10ML": 200,
    "DEXA-RHINASPRAY-N NASPR.SUS": 100,
    "DIOVAN F.C.TAB 40MG": 14,
    "OLFOSONIDE NASPR.SUS": 200,
    "VOLTAREN FAST PD.ORA.SOL 50M": 21,
    "INEPITANT CAPS 125MG/CAP+80MG/CAP BTX 1CAP 125MG + 2CAP 80MG ΣE  BLISTERS": 3,
    "VELTIFER OR.SOL.SD 100MG/5ML VIAL BTX10": 50,
    "CADELIUS OR.DISP.TA /TAB BOTTLEX30 TABS": 30,
    "COMTAN F.C.TAB 200MG/TAB ΦIAΛH X60": 60,
    "DEZEPIL DISP.TAB 100MG/TAB  ΔIΣKIA ΔIAΣΠ": 30,
    "DEZEPIL DISP.TAB 200MG/TAB  ΔIΣKIA ΔIAΣΠ": 30,
    "DEZEPIL DISP.TAB 25MG/TAB  ΔIΣKIA ΔIAΣΠ": 30,
    "ENIT TAB MG/TAB ΣYΣKEYAΣIA30 ΔIΣKIΩN": 30,
    "LEVODOPA+CARBIDOPA+ENTACAPONE/MYLAN F.C.TAB  MG/TAB BOTTLE  X 30": 30,
    "LEVODOPA+CARBIDOPA+ENTACAPONE/MYLAN F.C.TAB MG/TAB  BOTTLE  X 30": 30,
    "LOPRESOR F.C.TAB 100MG 4X10": 40,
    "NATECAL D3 1500  MG+400 IU/TAB BOTTLE X 60": 60,
    "NOVONORM TAB 1MG/TAB BLIST,X120": 120,
    "NOVONORM TAB 2MG/TAB BLIST,X120": 120,
    "OTEZLA F.C.TAB /TAB": 27,
    "SITAGLIPTIN+METFORMIN HYDROCHLORIDE MYLAN F.C.TAB MG/TAB  BT 56X1 TAB - MONAΔA ΔOΣHΣ ΣE BLISTERS": 56,
    "STALEVO F.C.TAB MG/TAB 1ΦIAΛH X30": 30,
    "STALEVO F.C.TAB MG/TAB BOTTLE  X 30": 30,
    "STALEVO F.C.TAB MG/TAB BOTTLE X 30": 30,
    "VALSART/HEREMCO F.C. TAB 160MG/TAB": 28,
    "VOKANAMET F.C.TAB MG/TAB HDPE BOTTLE X60": 60,
    "DIAZEPAM DESITIN  REC.SOL 5MG/TUB BTX5 RECTAL TUBES X 2,5ML": 12.5,
    "DELTIUS OR.SO.D 10000 IU/ML BTX1 X 10 ML": 10,
    "ΖIPTEK OR.SO.D 10MG/ML BOTTLE X 20 ML": 20,
    "LECALCIF OR.SO.D 2400 IU/ML BTX1X10MLX1": 10,
    "CLOPIXOL OR.SO.D 20MG/ML BTX1 VIALX20 ML": 20,
    "EFFORTIL OR.SO.D 7,5MG/ML BTX1VIAL X 15ML": 15,
    "ISOFREDIL OR.SO.D 100MG/ML BOTTLEX120ML": 120,
    "ISOFREDIL OR.SO.D 100MG/ML BOTTLEX60ML": 60,
    "RIVOTRIL OR.S.D. 2,5MG/ML BT X 1VIAL X 10ML": 10,
    "AEROLIN PD.INH.MD 200MCG/DOSE TAINIA X60 BLISTERS": 60,
    "AEROLIN NEBULES INH.SOL.N 2,5MG/2,5ML AMP  BTX20": 20,
    "AEROLIN NEBULES INH.SOL.N 5MG/2,5ML AMP  BTX20": 20,
    "AEROLIN NEBULES INH.SOL.N 2,5MG/2,5ML AMP  BTX10": 10,
    "AEROLIN NEBULES INH.SOL.N 5MG/2,5ML AMP  BTX10": 10,
    "ALVESCO INH.SOL.P 160MCG/DOSE": 120,  # max there is 60 as well
    "ANORO INH.PD.DOS MCG/DOSE BTX1 INHALER": 30,
    "AZODAL INH.SOL.P MCG/DOSE BTX1 ΣYΣKEYH EIΣΠNOΩN X120  ΔOΣOMETPHMENEΣ ΔOΣEIΣ": 120,
    "BOCACORT-S  INH.SUS.P 250MCG/DOSE BTX1BOTTLEX9G": 120,
    "BRONCOVENT INH.SOL.P 20MCG/DOSE BT X 1FL ME ΔOΣIMETPIKH BAΛBIΔA X10ML": 200,
    "DUAKLIR GENUAIR PD.INH.MD 340MCG + 12MCG BTX1 ΣYΣKEYH EIΣΠNOHΣ   X 60 MONAΔEΣ ENEPΓOΠOIHΣHΣ": 60,
    "FLIHALER INH.SUS.P 250MCG/DOSE ΣT,ΔOΣ, BTX1": 120,
    "FLIXOCORT INH.SUS.P 250MC/DOSE BTX1VIAL+M.VALV": 120,
    "FLIXOCORT INH.SUS.P 125MC/DOSE BTX1VIAL+M.VALV": 120,
    "FLIXOTIDE PD.INH.MD 250MCG/DOSE TAINIA X 60 BLISTERS": 60,
    "FLIXOTIDE PD.INH.MD 500MCG/DOSE TAINIA X 60 BLISTERS": 60,
    "FLIXOTIDE PD.INH.MD 100MCG/DOSE TAINIA X 60 BLISTERS": 60,
    "FLUTICAPEN INH.PD.DOS 250MC/DOSE BTX1": 60,
    "FLUTICAPEN INH.PD.DOS 500MC/DOSE BTX1": 60,
    "FORMOPEN INH.PD.DOS 12MCG/DOSE BTX1 EIΣΠNEYTIKH": 60,  # max there is 30 as well
    "FOSTER  NEXTHALER PD.INH.MD MCG/DOSE BTX": 120,
    "INUVAIR INH.SOL.P MC/DOSE": 120,
    "LAVENTAIR INH.PD.DOS MCG/DOSE BTX1 INHALER": 30,
    "NEBULIN INH.SUS.N 1,0MG/2ML BTX4 ΦAKEΛOYΣ X5": 20,
    "NEBULIN INH.SUS.N 0,5MG/2ML BTX4 ΦAKEΛOYΣ X5": 20,
    "NEBULIN INH.SUS.N 1,0MG/2ML BTX8 ΦAKEΛOYΣ X5": 40,
    "NEBULIN INH.SUS.N 0,5MG/2ML BTX8 ΦAKEΛOYΣ X5": 40,
    "PULMICORT INH.PD.DOS 200MCG/DOSE ΣYΣK, TURBUHALERX": 200,
    "PULMICORT INH.SUS.N 0,5MG/ML BTX40 ΠΛAΣT. ΦIAΛIΔIA  X2ML": 40,
    "PULMICORT INH.SUS.N 0,25MG/ML BTX40 ΠΛAΣT. ΦIAΛIΔIA": 40,
    "PULMICORT INH.SUS.N 0,5MG/ML BTX20 ΠΛAΣT. ΦIAΛIΔIA  X2ML": 20,
    "PULMICORT INH.SUS.N 0,25MG/ML BTX20 ΠΛAΣT. ΦIAΛIΔIA": 20,
    "PULMIHAL INH.SUS.P 200MCG/DOSE FLX10ML": 200,
    "PULMOZYME INH.SOL.N 2,500 U/2,5ML BTX6 ΠΛAΣTIKEΣ": 6,
    "ROLENIUM INH.PD.DOS MC/DOSE BT X 1 EIΣΠNEOMENH": 60,  # max there is 30 as well
    "SALENGA INH.SUS.P 250MCG/DOSE BTX1 BOTTLEX9G": 120,
    "SERETIDE  INH.SUS.P 25+125MCG/DOSE FLX12 G": 120,
    "SERETIDE  INH.SUS.P 25+250MCG/DOSE FLX12 G": 120,
    "SERETIDE  INH.SUS.P 25+50MCG/DOSE FLX12 G": 120,
    "SERETIDE DISKUS INH.PD.DOS MC/DOSE BTX1 DISKUSX60": 60,
    "SERETIDE DISKUS INH.PD.DOS MCG/DOSE BTX1 DISKUSX60": 60,
    "ULTIBRO BREEZHALER INHPD.CAP MCG/DOSE BTX30": 30,
    "XOTERNA BREEZHALER INHPD.CAP MCG/DOSE BTX30": 30,
    "ATROVENT INH.NE.SOL 250MCG/2ML BTX10": 10,
    "ATROVENT INH.SOL.N 500MCG/2ML  DOSE BTX10": 10,
    "ATROVENT AER.MD.INH 20MCG/DOSE FLX10ML": 200,
    "SERBO NASPR.SUS 100MC/DOSE FLX10 ML": 200,
    "FLUTINASAL NASPR.SUS 50MCG/DOSE BT x 1 BOTTLE x 16 G": 120,
    "FLUTINASAL NASPR.SUS 50MCG/DOSE BT x 1 BOTTLE x 8 G": 60,
    "MOMETASONE/TARGET NASPR.SUS 50MC/DOSE BTX1 FLX18 G": 140,
    "TALGAN NASPR.SUS 100MCG/DOSEΣTAΘ,ΔOΣ) FLX10ML": 200,
    "DYMISTA NASPR.SUS MG/G BTX1 ΦIAΛH X23G": 120,
    "VINECORT NASPR.SUS 100MC/DOSE BTX 1 VIAL X 10 ML": 200,
    "BIOSONIDE NASPR.SUS 100MCG/DOSE FLX10 ML": 200,
    "BIOSONIDE NASPR.SUS 50MCG/DOSE FLX10 ML": 200,
    "BIOSONIDE INH.SUS.N 0,5MG/2ML BTX30X2 ML": 30,
    "BIOSONIDE INH.SUS.N 1MG/2ML BTX30X2 ML": 30,
    "NASONEX NASPR.SUS 0,05% W/W BTX 1 FL X 18 G": 140,
    "NASONEX NASPR.SUS 0,05% W/W BT X 2 FL X 18 G": 280,
    "NASONEX NASPR.SUS 0,05% W/W BT X 3 FL X 18 G": 420,
    "OBECIROL NASPR.SUS 100MCG/DOSE BOTTLEX10ML": 200,
    "VERICORT NASPR.SUS 100MCG/DOSE BTX1FLX10ML": 200,
    "MIGRACOR NASPR.SOL 10MG/DOSE BTX1 VIAL X 1,8ML  ME  ΔOΣOMETPIKH ANTΛIA": 18,
    "BUDESONIDE/NORMA NASPR.SUS 100MC/DOSE BTX 1 FL X 10 ML": 200,
    "BUDESONIDE/NORMA NASPR.SUS 50MC/DOSE BTX 1 FL X 10 ML": 200,
    "FLUTARZOLE NASPR.SUS 50MC/DOSE FLX16 G": 120,
    "DYMISTA NASPR.SUS MG/G BTX1 ΦIAΛH X23G": 120,
    "DUPHALAC SYR 3,335G/5ML BOTTLEX300ML": 300,
    "DUPHALAC SYR 3,335G/5ML BOTTLEX1000ML": 1000,
    "DUPHALAC SYR 3,335G/5ML BOTTLEX5000ML": 5000,
    "DUPHALAC SYR 3,335G/5ML BTx10SACHETSx15 ML": 150,
    "ZARONTIN SYRUP 250MG/5ML BT X 1VIAL X 200ML": 200,
    "OTOSPON EA.SOL MG/1ML BTX 1 BOTTLE X 10 ML": 10,
    "PAROTICIN EA.SOL EA, SOL FL X 10ML": 10,
    "SYNALAR EA.SOL 0,25MG+5MG+10000IU/M FLX5 ML": 5,
    "CIPRATIC EA.SOL 1MG/0,5ML BTX20 AMPS  X 0,5ML": 10,
    "TRILEPTAL ORAL.SUSP 300MG/5ML BOTTLEX250ML": 250,
    "NITROFURANTOIN/IASIS ORAL.SUSP 25MG/5ML 1 BOTTLEX 300ML + 1 ΣYPIΓΓA  X 5ML +ΠPOΣAPMOΓEAΣ ΣYPIΓΓAΣ": 300,
    "NITROFURANTOIN/IASIS ORAL.SUSP 25MG/5ML 1 BOTTLEX 150ML + 1 ΣYPIΓΓA  X 5ML +ΠPOΣAPMOΓEAΣ ΣYPIΓΓAΣ": 150,
    "VOLTAREN FAST PD.ORA.SOL 50MG/SACHET SACHET 7X3": 21,
    "HELICOBACTER TEST INFAI  PD.ORA.SOL 75MG/JAR 1 JAR IN A KIT  WITH": 1,
    "SEVELAMER/FARAN F.C.TAB 800MG/TAB BTX BOTTLE  X 180": 180,
    "SEVELAMER/FARAN F.C.TAB 800MG/TAB BTX2 BOTTLE  X 180": 360,
    "ROTARIX ORAL.SUSP 1,5ML 1 ΣΩΛHNAPIO X 1,5ML": 1.5,
    "ROTATEQ ORAL.SOL  1 ΣΩΛHNAPIO  X2ML": 2,
    "SOLUMAG FORTE OR.SOL.SD 2,810G/10ML BTX20 VIALSX10 ML": 20,
    "OMALIN ORAL.SOL 800MG /15ML VIAL BTX10VIALSX15ML": 10,
    "OMALIN PLUS ORAL.SOL 800MG+0,200 MG/15ML VIAL BT X 10": 10,
    "BEROVENT INH.NE.SOL MG/2,5ML BTX30 ΦIAΛIΔIA AΠO": 30,
    "BEROVENT INH.NE.SOL MG/2,5ML BTX10 ΦIAΛIΔIA AΠO": 10,
    "ZYROLEN INH.SOL.N 250MCG/2ML AMP BTX30 AMPSX2 ML": 30,
    "ZYROLEN INH.SOL.N 500MCG/2ML AMP BTX30 AMPSX2 ML": 30,
    "ZYROLEN INH.SOL.N 250MCG/2ML AMP/DOSE BTX30 AMPSX2 ML": 30,
    "ZYROLEN INH.SOL.N 500MCG/2ML AMP/DOSE BTX30 AMPSX2 ML": 30,
    "ZYROLEN INH.SOL.N 250MCG/2ML AMP BTX10 AMPSX2 ML": 10,
    "ZYROLEN INH.SOL.N 500MCG/2ML AMP BTX10 AMPSX2 ML": 10,
    "ZYROLEN INH.SOL.N 250MCG/2ML AMP/DOSE BTX10 AMPSX2 ML": 10,
    "ZYROLEN INH.SOL.N 500MCG/2ML AMP/DOSE BTX10 AMPSX2 ML": 10,
    "AZATHIOPRINE/FARMASYN F.C.TAB 50MG/TAB BTX100": 100,
    "AZATHIOPRINE/PHARMACHEMIE TAB 50MG/TAB BTX100": 100,
    "FLUSONIDE INH.SUS.N 2MG/2ML BTX20  ΦYΣIΓΓEΣ  X 2ML": 20,
    "FLUSONIDE INH.SUS.N 0.5MG/2ML BTX20  ΦYΣIΓΓEΣ  X 2ML": 20,
    "MATRIFEN TTS 25MCG/H BTX5": 5,
    "ORGOVYX F.C.TAB 120MG/TAB BTX1 ΦIAΛH  X 30 ΔIΣKIA": 30,
    "ZENON F.C.TAB MG/TAB BTX1X30": 30,
    "KEPPRA ORAL.SOL 100MG/ML BTX1 ΦIAΛH X150ML": 150,
    "CONCERTA PR.TAB 36MG/TAB  BT X 1 BOTTLE X 30": 30,
    "ZAOFER EF.TAB 695MG /TAB BTX1 TUBX10": 10,
    "ZAOFER EF.TAB 695MG /TAB BTX3 TUBX10": 30,
    "ZAOFER EF.TAB 695MG /TAB BTX1 TUBX20": 20,
    "ZAOFER EF.TAB 695MG /TAB BTX3 TUBX20": 60,
    "GALANYL ORAL.SOL 4MG/ML BT X 1": 180,
    "OROMENTIS ORAL.SOL 2ML ORAL.SOL 2MG/ML  BTX1&ΔOΣOMETPIKO KOYTAΛI": 150,
    "ESOPRAZ GR.CAP 40MG/CAP1 BTX1 VIAL HDPE X 31 CAPS": 31,
    "VASCLOR VAG.GEL 8% W/W BTX1 TUBX22,5G+15APP": 15,
    "VASCLOR VAG.GEL 8% W/W BTX1 TUBX9,5G+5APP": 6,
    "LOMEXIN VAG.CR 0,02 BTX1TUBX78G+16": 16,
    "DALACIN C VAG.CR 2%  TUB X 40G": 7,
    "VELDOM VAG.CR 2% W/W BTXTUBX40G+7": 7,
    "CRINONE VAG.GEL 8%  BT X  6 APPLICATORS": 6,
    "CRINONE VAG.GEL 8%  BT X  15 APPLICATORS": 15,
    "BRETARIS GENUAIR INH.POWD 322MCG/DOSE 1 ΣYΣKEYH EIΣΠNOHΣ X 60": 60,
    "MENVEO P.SO.IN.SO 0,5ML  1 VIAL": 1,
    "VIOTICER EAR.DR.SUS % W/V BOTTLEX10ML": 10,
    "OPTISON INJ.AIR.MI 5-8X10/ML BTX1VIALX3ML": 1,
    # ΕΚΧΥΣΗ
    "APOTEL SOL.IV.INF 1G/6,7ML AMP BT X 3 AMPS X 6,7 ML": 3,
    "NIVESTIM INJ.SO.INF 48MU  5PF.SYRX0,5ML": 5,
    "PIPERACILLIN+TAZOBACTAM/KABI PD.SOL.INF 4G/0,500G VIAL X 50ML": 1,
    # CAPS
    "EMEND CAPS 125MG/CAP+80MG/CAP0 BLISTER  1CAP X": 3,
    # DROPS
    "DORZYLEA EY.DRO.SOL MG/ML BTX 30 FL  ΣTAΓONOMETPIKA SD  X0,3ML": 3,  # SOS (when σταγόνες in doctors prescription) We need to measure MLs to compare with the drug. When however is single dose containers they have more MLs but still count as the single dose (0.05 ml) for comparability. Considering both eyes we need to adjust for a more frugal approach, as if each single dose container has 0.1ml in. Finally, 30*0.1  # noqa: E501
    "HYALOVET PLUS EY.DR.S.SD 0,0975MG/0,65ML BTX30X0,65ML SINGLE DOSE  CONTAINERS": 3,  # Single dose containers comparing with σταγόνες  # noqa: E501
    "HYALOVET PLUS EY.DR.S.SD 0,0975MG/0,65ML BTX120X0,65ML SINGLE DOSE  CONTAINERS": 12,  # Single dose containers comparing with σταγόνες  # noqa: E501
    "CROMODAL EY.DRO.SOL 0,04 BT X 20": 2,  # Single dose containers comparing with σταγόνες
    "LATAZ-CO EY.DRO.SOL /ML BTX1": 2.5,
    "LATAZ-CO EY.DRO.SOL /ML BTX3": 7.5,
    "LATAZ-CO EY.DRO.SOL /ML BTX6": 15,
    "RESTASIS EY.DRO.SUS 0.05% 30 SINGLE DOSES X 0.4ML/V": 3,  # Single dose containers comparing with σταγόνες
    "DEXAFREE EY.DR.S.SD 1MG/ML BTX30X0,4ML": 3,  # Single dose containers comparing with σταγόνες
    "ZADITOR EY.DRO.SOL 0,25MG/1 ML BTX20": 2,  # Single dose containers comparing with σταγόνες
    "LUMIGAN EY.DRO.SOL 0,3MG/ML 1ΦIAΛIΔIO X3ML": 3,  # Single dose containers comparing with σταγόνες
    "OXATREX EY.DRO.SOL 1,5MG/0,5ML  BTX20": 2,  # Single dose containers comparing with σταγόνες
    "OXATREX EY.DRO.SOL 1,5MG/0,5ML  BTX10": 1,  # Single dose containers comparing with σταγόνες
    "GANFORT EY.DR.S.DC 300MG/ML-5MG/ML BTX30": 3,  # Single dose containers comparing with σταγόνες
    "TAPTIQOM EY.DR.S.DC /ML BTX30 SINGLE-DOSE CONTAINERS": 3,  # Single dose containers comparing with σταγόνες
    "LUMIGAN EY.S.SD 0,3MG/ML 30 ΠEPIEKTEΣ MIAΣ XPHΣHΣ": 3,  # Single dose containers comparing      NOT     σταγόνες
    "BRIMOFREE EY.DR.S.DC 2MG/ML BTX30 ΠEPIEKTEΣ MIAΣ ΔOΣHΣ LDPE X  0,35ML": 3,  # Single dose containers comparing with σταγόνες  # noqa: E501
    "FIXAPROST EY.DR.S.DC /ML BT X 30 CONTAINERS  ΦIAΛH  MIAΣ ΔOΣHΣ": 3,  # Single dose containers comparing with σταγόνες  # noqa: E501
    "UTENOS EY.DR.S.DC 0,25MG/ML BTX50 SDC  X0,4ML": 5,  # Single dose containers comparing with σταγόνες
    "MONOPROST EY.DR.S.SD 50MCG/ML BT X3 SACHETS X10 VIALS X0,2 ML": 3,  # Single dose containers comparing with σταγόνες  # noqa: E501
    "DROLL EAR.SO.S.D 1MG/0,5ML BTX20": 2,  # Single dose containers comparing with σταγόνες
    "AZARGA EY.DRO.SUS  MG/ML BTX 1ΦIAΛIΔIO": 5,
    "BRIMONTAL  EY.DRO.SOL 0,2%    BTX1": 5,
    "NEVANAC EY.DRO.SUS 1MG/ML BT X 1 BOTTLE": 5,
    "CORTIZI EY.DRO.SOL 3,35MG/ML VIALX10ML": 10,
    "VIZIDOR DUO EY.DRO.SOL MG/ML BTX1 ΦIAΛH  X5 ML": 5,
    "TRAV-IOP  EY.DRO.SOL 40MCG/ML BTXBOTTLEX2,5ML +  1 ΣTAΓONOMETPO": 2.5,
    "DUOTRAV EY.DRO.SOL 40MG/ML+5MG/ML BT X 1 ΦIAΛH X2,5ML": 2.5,
    "BUDENOFALK REC.FOAM 2MG/ACT.": 14,
    "GELTIM EYE.GEL 1MG/G BTX30 SINGLE-DOSE": 30,
    "STALORAL INITIAL MOUTH.DROP 0,1-1-10-100IR-IC/ML BT X 3 FLACON": 30,
    # ORAL.SOL
    "ABILIFY ORAL.SOL 1 MG/ML 1 ΦIAΛH X150ML": 150,
    "ABILIFY ORAL.SOL 1 MG/ML 1 ΦIAΛH X150ML": 150,
    "PREBANEL ORAL.SOL 20MG/ML 1ΦIAΛH  X473ML": 473,
    "KEPPRA ORAL.SOL 100MG/ML ΦIAΛH X 300ML": 300,
    "KAYEXALATE/SANOFI WINTHROP PD.ORA.SUS 454 G PLASTIC BOTTLE": 454,
    "LEGOFER OR.SOL.SD 800MG/15ML BT X 10": 150,
    "LEGOFER OR.SOL.SD 800MG/15ML BT X 20": 300,
    "LEGOFER OR.SOL.SD 1200MG/22,5ML BT X 10": 225,
    "LEGOFER OR.SOL.SD 1200MG/22,5ML BT X 20": 450,
    "BRIVIACT ORAL.SOL 10MG/ML 1 ΦIAΛH ΓYAΛINHX300ML": 300,
    "EPISTATUS  ORAL.SOL 10MG/1ML BT 1 X 5ML": 5,
    "LYRICA ORAL.SOL 20MG/ML 1ΦIAΛH  X473ML": 473,
    "NEO-CANDIMYK ORAL.SOL 10MG/ML VIALX150 ML": 150,
    # INJ.SOL
    "LEUPROL PS.INJ.SUS 11,25MG/VIAL KIT": 1,
    "MENQUADFI INJ.SOL MCG/0,5ML 1 VIALX0,5ML": 1,
    "APEXXNAR INJ.SUSP 0,5ML/PF.SYR 1 PF.SYR X 0,5ML + 1 BEΛONA": 1,
    "DEPIGOID  INJ.SUSP 1VIAL": 1,
    "DORMICUM INJ.SOL 15MG/3ML AMP BX 5 AMPS X 3 ML": 5,
    "ARVEKAP PS.INJ.SUS 11,25MG/VIAL BTXVIAL+1AMP SOLV+1AΠOΣTEIPΩMENH  ΣYPIΓΓA+1 AΠOΣTEIPΩMENH BEΛONA 0,9MM": 1,
    "ARVEKAP PS.INJ.SUS 3,75MG/VIAL BTXVIAL+1AMP SOLV+1AΠOΣTEIPΩMENH  ΣYPIΓΓA+1 AΠOΣTEIPΩMENH BEΛONA 0,9MM": 1,
    "HAVRIX 720ELISA UNITS/DOSE  INJ.SUSP BTX1PF.SYRX0,5ML": 1,
    "HAVRIX 1440 ELISA UNITS/DOSE INJ.SUSP, BTX1PF.SYR X 1ML": 1,
    "ADDAMEL N NEW C/S.SOL.IN  1 BOX X20AMP X10ML": 20,
    "COSENTYX INJ.SOL 300MG/2ML 1 PF.PEN X2ML": 1,
    "DYNASTAT PS.INJ.SOL 40MG/VIAL 1VIALX40MG": 1,
    "TRULICITY INJ.SOL 1,5MG BTX2 PF.PEN": 2,
    "TRULICITY INJ.SOL 0,75MG BTX2 PF.PEN": 2,
    "TRULICITY INJ.SOL 3MG BTX2 PF.PEN": 2,
    "TRULICITY INJ.SOL 4.5MG BTX2 PF.PEN": 2,
    "PROLIA INJ.SOL 60MG/ML  BT X 1PF SYR": 1,
    "OZEMPIC INJ.SOL 0,25MG/0,19  1,34MG/ML 1 ΠP. ΣYΣK. TYΠOY  ΠENAΣX1,5ML+4 BEΛONEΣ": 4,
    "OZEMPIC INJ.SOL 0,5MG/0,37  1,34MG/ML 1 ΠP. ΣYΣK. TYΠOY  ΠENAΣX1,5ML+4 BEΛONEΣ": 4,
    "OZEMPIC INJ.SOL 1MG/0,74  1,34MG/ML 1 ΠP. ΣYΣK. TYΠOY  ΠENAΣX1,5ML+4 BEΛONEΣ": 4,
    "OZEMPIC INJ.SOL 0,5 MG/0,37 ML BT X 1 PRE-FILLED PENS X 0,37ML + 4  DISPOSABLE NEEDLES": 4,
    "SCANLUX INJ.SOL 300MG BOTTLEX100ML": 100,
    "SCANLUX INJ.SOL 300MG BOTTLEX50ML": 50,
    "SCANLUX INJ.SOL 370MG BOTTLEX100ML": 100,
    "XENETIX INJ.SOL 548,4MG/ML BOTTLE X 50 ML": 50,
    "XENETIX INJ.SOL 548,4MG/ML BOTTLE X 100 ML": 100,
    "XENETIX INJ.SOL 548,4MG/ML BOTTLE X 200 ML": 200,
    "XENETIX INJ.SOL 658,1MG/ML BOTTLE X 50 ML": 50,
    "XENETIX INJ.SOL 658,1MG/ML BOTTLE X 100 ML": 100,
    "XENETIX INJ.SOL 658,1MG/ML BOTTLE X 200 ML": 200,
    "XENETIX INJ.SOL 767,8MG/ML BOTTLE X  50 ML": 50,
    "XENETIX INJ.SOL 767,8MG/ML BOTTLE X 100 ML": 100,
    "XENETIX INJ.SOL 767,8MG/ML BOTTLE X 200 ML": 200,
    "IOMERON INJ.SOL 30%  W/V BOTTLE X 50 ML": 50,
    "IOMERON INJ.SOL 30%  W/V BOTTLE X 100 ML": 100,
    "IOMERON INJ.SOL 30% W/V BOTTLE X 150 ML": 150,
    "IOMERON INJ.SOL 30%  W/V BOTTLE X 200 ML": 200,
    "IOMERON INJ.SOL 30% W/V BOTTLE X 500 ML": 500,
    "IOMERON INJ.SOL 35% W/V BOTTLE X 50 ML": 50,
    "IOMERON INJ.SOL 35% W/V BOTTLE X 100 ML": 100,
    "IOMERON INJ.SOL 35% W/V BOTTLE X 150 ML": 150,
    "IOMERON INJ.SOL 35% W/V BOTTLE X 200 ML": 200,
    "IOMERON INJ.SOL 35% W/V BOTTLE X 500 ML": 500,
    "IOMERON INJ.SOL 40% W/V BOTTLE X 50 ML": 50,
    "IOMERON INJ.SOL 40% W/V BOTTLE X 100 ML": 100,
    "IOMERON INJ.SOL 40% W/V BOTTLE X 150 ML": 150,
    "IOMERON INJ.SOL 40% W/V BOTTLE X 200 ML": 200,
    "IOMERON INJ.SOL 40% W/V BOTTLE X 500 ML": 500,
    "FILGRASTIM HEXAL INJ.SO.INF 48MU  BTX5 PF SYR X 0,5 ML": 5,
    "FILGRASTIM HEXAL INJ.SO.INF 30MU  BTX5 PF SYR X 0,5 ML": 5,
    "TREVICTA INJ.SU.RET 350MG/PF SYR 1 PFSYR X 1,750 ML  + 2  BEΛONEΣ": 1,
    "TREVICTA INJ.SU.RET 525MG/PF SYR 1 PFSYR X 2,625 ML  + 2  BEΛONEΣ": 1,
    "VAXNEUVANCE INJ.SUSP 0,5ML/PFS 1 PF.SYR X 0,5ML  + 2  ΞEXΩPIΣTEΣ BEΛONEΣ": 1,
    "FLUCELVAX TETRA INJ.SUSP.  MCG/0,5/ML": 1,
    "FLUAD TETRA INJ.SUSP MCG/0,5ML PF.SYR  1 PF.SYR ME  BEΛONA": 1,
    "ALOPERIDIN DECANOAS INJ.SOL 50MG/1 ML AMP BTX 1 AMP X 3ML": 150,
    "FERRINEMIA IN.SO.CR 20MG/1ML": 5,
    # Insulin needs rethinking. At the moment it is as if we do not check it as it gets BTX and messes things up. Huge deviations from what pharmacists give.  # noqa: E501
    "VICTOZA IN.SO.PF.P 6MG/ML BTX1 PF PENS X3ML": 18,
    "VICTOZA IN.SO.PF.P 6MG/ML BTX2 PF PENS X3ML": 36,
    "VICTOZA IN.SO.PF.P 6MG/ML BTX3 PF PENS X3ML": 54,
    "TRESIBA INJ.SOL 100U/ML 5 PF.PEN-ΓYAΛIX3ML": 1500,
    "TOUJEO  IN.SO.PF.P 300 UNITS/ML BTX3 PF.PENS   X1,5ML": 1350,
    "TOUJEO  IN.SO.PF.P 300 UNITS/ML BT X 3 PF. PEN  X 3ML": 2700,
    "XULTOPHY IN.SO.PF.P /ML BTX 3 PF.PEN X 3ML": 900,
    "LYUMJEV INJ.SOL 100IU/ML BT X 5PF.PEN X 3ML  KWIKPEN": 1500,
    "LYUMJEV INJ.SOL 200IU/ML BT X 5PF.PEN X 3ML  KWIKPEN": 3000,
    "LYUMJEV JUNIOR KWIKPEN INJ.SOL 100IU/ML BT X 5PF.PEN X 3ML": 1500,
    "LYUMJEV INJ.SOL 100IU/ML BTX 1 VIAL X 10ML": 1000,
    "ABASAGLAR INJ.SOL 100U/ML BTX5 PF.PENX3ML": 1500,
    "ABASAGLAR INJ.SOL 100U/ML 2 BTX5 PF.PEN X3ML - ΠOΛYΣYΣKEYAΣIA": 3000,
    "ABASAGLAR INJ.SOL 100U/ML BTX10 CARTRIDGES X 3ML": 3000,
    "LANTUS INJ.SOL 100 IU/ML BTX3 PF PEN SOLOSTAR": 900,
    "LANTUS INJ.SOL 100 IU/ML BTX5 PF PEN SOLOSTAR": 1500,
    "LANTUS INJ.SOL 100 IU/ML BTX10 PF PEN SOLOSTAR": 3000,
    "LANTUS INJ.SOL 100 IU/ML CARTR,3ML BTX5CARTR,X3ML": 1500,
    "APIDRA INJ.SOL 100 IU/ML BT X 3 PF PEN SOLOSTAR": 900,
    "APIDRA INJ.SOL 100 IU/ML BT X 5 PF PEN SOLOSTAR": 1500,
    "APIDRA INJ.SOL 100 IU/ML BT X 10 PF PEN SOLOSTAR": 3000,
    "LEVEMIR IN.SO.PF.P 100 U/ML FLEXPEN 5 PF,PEN X 3 ML": 1500,
    "LEVEMIR PENFILL INJ.SOL 100 U/ML BTX5CARTRIDGES": 2130,
    "HUMALOG INJ.SOL 100 U/ML BTX1VIALX10ML": 1000,
    "HUMALOG  INJ.SOL 100 IU/ML BTX 5 PF PEN X 3ML": 1500,
    "HUMALOG  INJ.SUSP 100 U/ML BTX 5 PF PEN X 3ML": 1500,
    "HUMALOG-CARTRIDGE INJ.SOL 100 U/ML BTX5 CARTR,X3ML": 1500,
    "HUMALOG KWIKPEN INJ.SOL 200 U/ML BTX5 PF.PEN X3ML": 3000,
    "HUMULINCARTRIDGE INJ.SUSP 100IU/ML  BTX5CARTR,X3ML ΓIA": 1500,
    "HUMULINCARTRIDGE INJ.SOL 100 IU/ML  BTX5CARTR,X3ML  ΓIA": 1500,
    "HUMULIN NPH INJ.SUSP 100IU/ML BTX1 VIAL X 10 ML": 1000,
    "HUMULIN REGULAR INJ.SOL 100IU/ML BTX1 VIAL X 10 ML": 1000,
    "HUMULIN M3 CARTRIDGE INJ.SUSP 100 IU/ML BT  X 5 CARTRIDGES X": 1500,
    "FIASP INJ.SOL 100U/ML ΠPOΓEMIΣMENH ΣYΣKEYH TYΠOY ΠENAΣ 5 PF.PENX3ML": 1500,
    "FIASP INJ.SOL 100U/ML 1 VIAL  X 10ML": 1000,
    "NOVORAPID FLEX PEN INJ.SOL 100 U/ML 5PF,SYR,X3ML": 1500,
    "NOVORAPID PENFILL INJ.SOL 100U/ML 5CARTRIDGESX3ML": 1500,
    "NOVORAPID INJ.SOL 100U/ML 1VIALX10ML": 1000,
    "ACTRAPID PENFILL 100 IU/ML INJ.SOL 100 IU/ML 5ΓYAΛ,ΦIAΛ,X3ML": 1500,
    "ACTRAPID - 100 IU/ML INJ.SOL 100IU/ML 1ΓYAΛ,ΦIAΛ,X10ML": 1000,
    "NOVOMIX 30 FLEXPEN INJ.SUSP 100 U/ML 5 ΠPOΓEMIΣMENEΣ": 1500,
    "MIXTARD 30 PENFILL-100IU/ML INJ.SUSP 100 IU/ML 5 ΓYAΛ,ΦYΣIΓ,X3ML": 1500,
    "MIXTARD 40 PENFILL-100IU/ML INJ.SUSP 100 IU/ML 5 ΓYAΛ,ΦYΣIΓ,X3ML": 1500,
    "MIXTARD 50 PENFILL-100IU/ML INJ.SUSP 100 IU/ML 5 ΓYAΛ,ΦYΣIΓ,X3ML": 1500,
}


def find_product_in_description(description: str) -> float:
    """
    Searches a given description for product names and returns their respective amounts.

    Args:
        products (dict): A dictionary with product names as keys and their respective amounts as values.
        description (str): The description in which to search for product names.

    Returns:
        float: The amount of the product if the product name is found in the description,
        or 0 if no product names are found.
    """
    # Ensure description is a string and remove leading/trailing whitespace
    if not isinstance(description, str):
        return UNABLE_TO_IDENTIFY
    description = description.strip()

    for product, amount in product_list.items():
        # Ensure product is a string and remove leading/trailing whitespace
        if not isinstance(product, str):
            continue
        product = product.strip()

        # Search for product as a whole word (not a substring of another word)
        if re.search(r"\b" + re.escape(product) + r"\b", description, re.IGNORECASE):
            return amount

    return UNABLE_TO_IDENTIFY


def number_word_list(description: str, words: list[str]) -> float:
    """
    Extracts the first number preceding a keyword in a given string.

    Args:
        description (str): The input string.
        words (List[str]): List of keywords.

    Returns:
        float: The first number preceding a keyword, 0 if not found.
    """
    # Removes all whitespaces from the description string.
    trimmed_description = re.sub(r"\s+", "", description)

    # Creates a regex pattern that matches any number followed by any word from the given list.
    # The pattern will look like "[0-9]+word1|[0-9]+word2|...|[0-9]+wordN".
    pattern = re.compile("|".join([f"[0-9]+{word}" for word in words]))

    # Finds all matches of the pattern in the trimmed_description.
    matches = re.findall(pattern, trimmed_description)

    # Takes the first match from the list of matches.
    first_match = matches[0]

    # Removes the word part from the first_match, leaving only the number part.
    # For example, if first_match is "3cats", number will be "3".
    number = re.sub("|".join(words), "", first_match)

    # Checks if the resulting string is a number (only contains digits).
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def number_metered_doses(description: str) -> float:
    return number_word_list(description, words=["METEREDDOSES"])


def number_actuations(description: str) -> float:
    return number_word_list(description, words=["ACTUATIONS"])


def number_sprays(description: str) -> float:
    return number_word_list(description, words=["ΨEKAΣMOI", "ΨEKAΣMOI"])


def number_prototype(description: str) -> float:
    return number_word_list(description, words=["ΠΡΩΤΟΤΥΠΟ", "ΠPΩTOTYΠO"])


def number_inhalations(description: str) -> float:
    return number_word_list(description, words=["EIΣΠNOEΣ", "EIΣΠNOEΣ"])


def number_doses(description: str) -> float:
    return number_word_list(description, words=["DOSES", "ΔOΣEIΣ", "ΔOΣH", "ΔOΣEIΣ", "ΔOΣH"])  # unicode chars


def number_caps(description: str) -> float:
    return number_word_list(description, words=["CAPS"])


def number_disks(description: str) -> float:
    return number_word_list(description, words=["ΔIΣKIΩN", "ΔIΣKIΩN"])


def bt_x_number_appl_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile("BTX([0-9]+)")
    matches = re.findall(pattern, trimmed_description)
    if matches:
        number = matches[0]
    else:
        return UNABLE_TO_IDENTIFY
    pattern = re.compile("APPLX([0-9]+)")
    matches = re.findall(pattern, trimmed_description)
    if matches:
        second_number = matches[0]
    else:
        return UNABLE_TO_IDENTIFY
    if number.isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def doses_number_ml(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile(r"[0-9]+MLBTX")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("MLBTX", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def plus_number_appl(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile(r"\+[0-9]+APPL")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("APPL", "", first_match).replace("+", "")
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def plus_number_prototype(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile(r"\+[0-9]+ΠPOTOTYΠO")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("ΠPOTOTYΠO", "", first_match).replace("+", "")
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def number_ml_bt_x_number(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile(r"([0-9]+[.,]?[0-9]*)ML")  # Updated to include dot and comma as decimal separators
    matches = re.findall(pattern, trimmed_description)
    number = re.sub("ML", "", matches[0]).replace(",", ".")  # Replace comma with dot to make it a valid float
    pattern = re.compile("BTX([0-9]+)")
    matches = re.findall(pattern, trimmed_description)
    second_number = matches[0]
    if number.replace(".", "").isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def bt_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile(r"BTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def ml_bt_x_number_amp(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile(r"ML\s*BTX(\d+)AMP")
    matches = re.findall(pattern, trimmed_description)
    # first_match = matches[0]
    number = re.sub("BTX", "", matches[0])
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def cap_bt_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile(r"CAP\s*BTX(\d+)")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


# watch out ROLENIUM should not be included
def dose_bt_x_number(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile(r"DOSE\s*BTX(\d+)")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def vial_bt_x_number(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile("VIALBTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("VIALBTX", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


def bt_x_number_blist_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile("BTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    pattern = re.compile("BLISTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    second_number = re.sub("BLISTX", "", matches[0])
    if number.isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def bt_x_number_fl_x_number(description: str) -> float:
    trimmed_description = re.sub(r"\s+", "", description)
    pattern = re.compile("BTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    pattern = re.compile("FLX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    second_number = re.sub("FLX", "", matches[0])
    if number.isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def bt_x_number_x_number_vials(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    trimmed_description = trimmed_description.replace("SACHETS", "")
    pattern = re.compile("BTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    pattern = re.compile("X[0-9]+VIALS")
    matches = re.findall(pattern, trimmed_description)
    second_number = re.sub("XVIALS", "", matches[0]).replace("X", "").replace("VIALS", "")
    if number.isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def bt_x_number_vial_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile("BTX[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BTX", "", first_match)
    pattern = re.compile("VIALX[0-9]+|VIALSX[0-9]+|ΦΙΑΛΕΣ[0-9]+|ΦΙΑΛΗ[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    second_number = re.sub("VIALX|VIALSX|ΦΙΑΛΕΣ|ΦΙΑΛΗ", "", matches[0]).split("CAPS")[0]
    if number.isdigit() and second_number.isdigit():
        return float(number) * float(second_number)
    return UNABLE_TO_IDENTIFY


def bottle_x_number(description: str) -> float:
    trimmed_description = re.sub(r"[,\s]+", "", description)
    pattern = re.compile("BOTTLE(?:S)?X[0-9]+")
    matches = re.findall(pattern, trimmed_description)
    first_match = matches[0]
    number = re.sub("BOTTLE(?:S)?X", "", first_match)
    if number.isdigit():
        return float(number)
    return UNABLE_TO_IDENTIFY


# Already touched upon but need further improvement


def bt_x_number_fl_x_ml(description: str) -> float:
    # Normalize the description by removing spaces and converting to a consistent format
    trimmed_description = re.sub(r"\s+", "", description).replace(",", ".")

    # Compile patterns to find the number of bottles and volume per bottle
    pattern_bt = re.compile(r"BTX(\d+)", re.IGNORECASE)
    pattern_fl = re.compile(r"FLX(\d+(?:\.\d+)?)ML", re.IGNORECASE)

    # Find matches for both patterns
    matches_bt = pattern_bt.search(trimmed_description)
    matches_fl = pattern_fl.search(trimmed_description)

    if matches_bt and matches_fl:
        # Extract numbers from matches and convert them to float
        number_bt = int(matches_bt.group(1))
        number_fl_ml = float(matches_fl.group(1))

        # Calculate the total volume
        total_volume = number_bt * number_fl_ml
        return total_volume

    return UNABLE_TO_IDENTIFY


# ______________________________________________________________________________________________________
# NEW Revamped functions
# Taking into consideration 0 value
# Taking into consideration that the numbers may be decimals comma or dot such as 2.5 or 2,5


def fl_x_number(description: str) -> float:
    # Standardize decimal separator to dot and remove spaces, make case-insensitive
    trimmed_description = re.sub(r"\s+", "", description.replace(",", "."), flags=re.IGNORECASE)
    # Update the pattern to match decimal numbers after "FLX" with case-insensitive flag
    pattern = re.compile(r"FLX(\d+(?:\.\d+)?)", re.IGNORECASE)
    matches = re.findall(pattern, trimmed_description)

    if matches:
        number = matches[0]
        # Convert the extracted number to float
        number_float = float(number)
        # Check if the number is 0
        if number_float == 0:
            return UNABLE_TO_IDENTIFY
        else:
            return number_float

    # Return this if no valid number is found
    return UNABLE_TO_IDENTIFY


def bt_x_number_sachet_x_number(description: str) -> float:
    # Normalize decimal separators: replace commas with periods
    normalized_description = description.replace(",", ".")

    # Adjusting for case-insensitivity in regex matching
    normalized_description = re.sub(r"\s+", " ", normalized_description)  # Normalize spaces too

    # Pattern to match numbers (assuming decimal separator is always a period)
    bt_pattern = re.compile("BTX(\d+(?:\.\d+)?)", re.IGNORECASE)  # noqa: W605
    bt_match = bt_pattern.search(normalized_description)

    sachet_pattern = re.compile("SACHETS? X (\d+(?:\.\d+)?)", re.IGNORECASE)  # noqa: W605
    sachet_match = sachet_pattern.search(normalized_description)

    if bt_match and sachet_match:
        bt_number = float(bt_match.group(1))
        sachet_number = float(sachet_match.group(1))

        # Check if either number is 0, indicating an incorrect input
        if bt_number == 0 or sachet_number == 0:
            return UNABLE_TO_IDENTIFY

        return bt_number * sachet_number

    return UNABLE_TO_IDENTIFY


def bt_x_number_bottle_x_ml(description: str) -> float:
    # Normalize decimal separators to a single format (e.g., replacing ',' with '.')
    # and remove extra spaces without affecting the decimal separator handling
    description = re.sub(r"\s+", "", description)  # Remove all whitespace
    description = description.replace(",", ".")  # Standardize decimal separator

    # Adjusted patterns to capture decimal numbers and ensure 'ML' is at the end
    pattern_bt = re.compile(r"BTX(\d+(?:\.\d+)?)", re.IGNORECASE)
    pattern_bottle = re.compile(r"BOTTLE(?:S)?X(\d+(?:\.\d+)?)ML$", re.IGNORECASE)

    matches_bt = re.findall(pattern_bt, description)
    matches_bottle = re.findall(pattern_bottle, description)

    if matches_bt and matches_bottle:
        number_bt = float(matches_bt[0])
        number_bottle_ml = float(matches_bottle[0])

        # Check for zero values to avoid returning 0 as a result
        if number_bt == 0 or number_bottle_ml == 0:
            return UNABLE_TO_IDENTIFY

        return number_bt * number_bottle_ml

    return UNABLE_TO_IDENTIFY


def bt_x_number_vial_x_number_ml(description: str) -> float:
    # Normalize the description to simplify matching, convert to uppercase and handle decimal separators uniformly
    description = description.upper().replace(",", ".")

    # Pattern for BT number, allowing for optional spaces and decimals
    bt_pattern = re.compile(r"BT\s*X\s*(\d+(?:\.\d+)?)")
    vial_pattern = re.compile(r"VIAL(S)?\s*X\s*(\d+(?:\.\d+)?)\s*ML")

    bt_match = bt_pattern.search(description)
    vial_match = vial_pattern.search(description)

    if bt_match and vial_match:
        bt_number = float(bt_match.group(1))
        vial_number = float(vial_match.group(2))

        # Check if either number is 0
        if bt_number == 0 or vial_number == 0:
            return UNABLE_TO_IDENTIFY

        return bt_number * vial_number

    # Return this if patterns do not match or if any number is 0
    return UNABLE_TO_IDENTIFY


def bt_x_number_bottle_x_number(description: str) -> float:
    # Standardize decimal separator to '.' and remove excessive spaces
    # Make the description case-insensitive
    description = re.sub(r"\s+", " ", description.replace(",", "."), flags=re.IGNORECASE).strip()

    # Updated patterns to match the BTX and BOTTLE X parts with optional decimal points
    pattern_bt = re.compile(r"BTX\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
    pattern_bottle = re.compile(r"BOTTLE\s*X\s*([0-9]+(?:\.[0-9]+)?)(?:\s*TABS)?", re.IGNORECASE)

    # Find matches for both patterns
    matches_bt = re.findall(pattern_bt, description)
    matches_bottle = re.findall(pattern_bottle, description)

    # Check if both matches are found
    if matches_bt and matches_bottle:
        # Extract numbers from matches and convert to float to handle decimals
        number_bt = float(matches_bt[0])
        number_bottle_unit = float(matches_bottle[0])

        # Check for zero values to avoid returning 0 as a result
        if number_bt == 0 or number_bottle_unit == 0:
            return UNABLE_TO_IDENTIFY

        # Calculate total quantity considering decimals
        return number_bt * number_bottle_unit

    # Return a specific value to indicate the quantity could not be identified
    return UNABLE_TO_IDENTIFY


def data_corel_issue(description: str) -> float:  # noqa: [U100]
    return UNABLE_TO_IDENTIFY


def dosage_excluded(description: str) -> float:  # noqa: [U100]
    return NO_NEED_TO_IDENTIFY


def extract_from_rules(
    description: str, rules: list[Callable[[str], float]]
) -> tuple[float, Optional[Callable[[str], float]]]:
    for rule in rules:
        try:
            res: float = rule(description)
        except IndexError:
            continue
        if res != UNABLE_TO_IDENTIFY:
            return res, rule
    return UNABLE_TO_IDENTIFY, None


rules_dictionary: dict[str, list[Callable[[str], float]]] = {
    "ΔΕΡΜ": [find_product_in_description, dosage_excluded],  # disclaimer
    "ΟΦΘ.ΕΠΑΛΕΙΨΗ": [find_product_in_description, dosage_excluded],
    "ΕΠΑΛΕΙΨΗ": [find_product_in_description, dosage_excluded],
    "ΡΙΝΙΚΑ": [find_product_in_description, dosage_excluded],
    "ΔΙΑΔΕΡΜ": [find_product_in_description, bt_x_number],
    "ΔΙΣΚΙΑ": [
        find_product_in_description,
        bt_x_number_blist_x_number,
        number_disks,
        bt_x_number_fl_x_number,
        bt_x_number_bottle_x_number,
        fl_x_number,
        bt_x_number,
    ],
    "ΔΙΣΚΙΟ": [
        find_product_in_description,
        bt_x_number_blist_x_number,
        number_disks,
        bt_x_number_fl_x_number,
        fl_x_number,
        bt_x_number,
    ],
    "ΔΙΣΚΙΑ-ΔΙΑΣΠ": [
        find_product_in_description,
        bt_x_number_blist_x_number,
        number_disks,
        bt_x_number_fl_x_number,
        fl_x_number,
        bt_x_number,
    ],
    "ΕΙΣΠΝOΕΣ": [
        find_product_in_description,
        number_metered_doses,
        number_actuations,
        number_sprays,
        number_inhalations,
        number_caps,
        number_doses,
        ml_bt_x_number_amp,
        vial_bt_x_number,
        bt_x_number_appl_x_number,
        cap_bt_x_number,
    ],
    "ΕΙΣΠΝΟΕΣ": [
        find_product_in_description,
        number_metered_doses,
        number_actuations,
        number_sprays,
        number_inhalations,
        number_caps,
        number_doses,
        ml_bt_x_number_amp,
        vial_bt_x_number,
        bt_x_number_appl_x_number,
        cap_bt_x_number,
    ],
    "ΕΚΧΥΣΗ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΕΝΕΣΗ": [find_product_in_description, bt_x_number],
    "ΕΝΕΣΙΜΗ": [
        find_product_in_description,
    ],
    "ΕΝΕΣΙΜΟ": [find_product_in_description],
    "ΚΑΨΑΚΙΟ": [find_product_in_description, bt_x_number],
    "ΚΑΨΑΚΙΟ,": [find_product_in_description, bt_x_number],
    "ΚΑΨΑΚΙΑ": [find_product_in_description, bt_x_number],
    "ΚΑΨΟΥΛΑ": [find_product_in_description, bt_x_number_blist_x_number, bt_x_number],
    "ΚΑΨΟΥΛΕΣ": [find_product_in_description, bt_x_number_vial_x_number, fl_x_number, bt_x_number],
    "ΚΟΛΠΙΚΗ": [
        find_product_in_description,
        plus_number_prototype,
        plus_number_appl,
    ],
    "ΚΟΛΠΙΚΟ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΚΟΝΙΣ": [
        find_product_in_description,
        number_doses,
        bt_x_number,
    ],
    "ΟΡΘΙΚΗ": [
        find_product_in_description,
    ],
    "ΟΡΘΙΚΟΣ": [
        find_product_in_description,
    ],
    "ΟΦΘ.ΣΤΑΓΟΝΕΣ": [
        find_product_in_description,
        bt_x_number_bottle_x_ml,
        bt_x_number_vial_x_number_ml,
        bt_x_number_fl_x_ml,
        fl_x_number,
    ],
    "ΟΦΘΑΛΜΙΚΕΣ": [
        find_product_in_description,
        bt_x_number_bottle_x_ml,
        bt_x_number_vial_x_number_ml,
        bt_x_number_fl_x_ml,
        fl_x_number,
    ],
    "ΠΟΣ": [
        find_product_in_description,
        bt_x_number_vial_x_number_ml,
        bt_x_number_vial_x_number,
        bt_x_number_bottle_x_ml,
        bt_x_number_fl_x_ml,
        bottle_x_number,
        doses_number_ml,
        fl_x_number,
        bt_x_number,
    ],
    "ΠΟΣ.ΔΙΑΛ": [
        find_product_in_description,
        bt_x_number_vial_x_number_ml,
        bt_x_number_vial_x_number,
        bt_x_number_bottle_x_ml,
        bt_x_number_fl_x_ml,
        bottle_x_number,
        doses_number_ml,
        fl_x_number,
        bt_x_number,
    ],
    "ΠΟΣ.ΔΙΑΛΥΜΑ": [
        find_product_in_description,
        bt_x_number_vial_x_number_ml,
        bt_x_number_vial_x_number,
        bt_x_number_bottle_x_ml,
        bt_x_number_fl_x_ml,
        bottle_x_number,
        doses_number_ml,
        fl_x_number,
        bt_x_number,
    ],
    "ΠΟΣ.ΣΚΟΝΗ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΠΟΣ.ΣΤΑΓΟΝΕΣ": [
        find_product_in_description,
        bt_x_number_bottle_x_ml,
        bt_x_number_fl_x_ml,
        fl_x_number,
    ],
    "ΠΟΣΙΜΕΣ": [
        find_product_in_description,
        bt_x_number_bottle_x_ml,
        bt_x_number_vial_x_number_ml,
        bt_x_number_fl_x_ml,
        fl_x_number,
    ],
    "ΥΠΟΓΛΩΣΣΙΕΣ": [find_product_in_description, bt_x_number_vial_x_number_ml, bt_x_number_fl_x_ml],
    "ΕΝΑΙΩΡΗΜΑ": [
        find_product_in_description,
    ],
    "ΡΙΝΙΚΟ": [
        find_product_in_description,
        number_sprays,
        number_doses,
    ],
    "ΣΙΡΟΠΙ": [
        find_product_in_description,
        bt_x_number_bottle_x_ml,
        fl_x_number,
    ],
    "ΥΠΟΘΕΤΑ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΦΑΚΕΛΑΚΙ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΟΤΙΚΟ": [
        find_product_in_description,
    ],
    "ΕΜΦΥΤΕΥΣΗ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΣΚΟΝΗ": [
        find_product_in_description,
        bt_x_number,
    ],
    "ΕΜΠΛΑΣΤΡΟ": [
        find_product_in_description,
        bt_x_number_sachet_x_number,
    ],
    "ΕΝΕΜΑ": [
        find_product_in_description,
        bt_x_number_fl_x_number,
    ],
    "ΔΟΣΕΙΣ": [find_product_in_description],
    "g": [dosage_excluded],
    "γ": [dosage_excluded],
    "γρ": [dosage_excluded],
    "ΓΡ": [dosage_excluded],
    "GR": [dosage_excluded],
    "gr": [dosage_excluded],
    "G": [dosage_excluded],
    "ΓΡΑΜΜΑΡΙΑ": [dosage_excluded],
    "ΜG": [find_product_in_description, dosage_excluded],
    "mg": [find_product_in_description, dosage_excluded],
    "ml": [find_product_in_description, dosage_excluded],
    "ML": [find_product_in_description, dosage_excluded],
    "": [dosage_excluded],
}


def number_of_products_per_container(
    product_type: str, description: str
) -> tuple[float, Optional[Callable[[str], float]]]:
    try:
        return extract_from_rules(description, rules_dictionary[product_type])
    except KeyError:
        return UNABLE_TO_IDENTIFY, None


def clean_description(description: str) -> str:
    return (
        re.sub(r"\([^)]*\)", "", description)
        .upper()
        .replace("Χ", "X")
        .replace("Α", "A")
        .replace("Ε", "E")
        .replace("Ι", "I")
        .replace("Υ", "Y")
        .replace("Ο", "O")
        .replace("Η", "H")
        .replace("Ό", "O")
        .replace("Ί", "I")
        .replace("Ά", "A")
        .replace("Έ", "E")
        .replace("Ή", "H")
        .replace("Ύ", "Y")
        .replace("Τ", "T")
        .replace("Β", "B")
        .replace("Μ", "M")
        .replace("Ρ", "P")
        .replace("Ν", "N")
        .replace("Κ", "K")
        .strip()
    )


def number_of_products_per_container_api(
    substance_administration: SubstanceAdministration,
) -> tuple[float, Optional[Callable[[str], float]]]:
    try:
        # TODO: add to mandatory fields check
        #  substance_administration.consumable.name and substance_administration.consumable.form_code.translation
        clear_description = clean_description(substance_administration.consumable.name)
        api_rules_dictionary = deepcopy(rules_dictionary)
        api_rules_dictionary["ΕΙΣΠΝΟΕΣ_ΔΙΑΛ_ΔΟΣΕΙΣ"] = rules_dictionary["ΕΙΣΠΝΟΕΣ"]
        api_rules_dictionary["ΕΙΣΠΝΟΕΣ_ΔΟΣΕΙΣ"] = rules_dictionary["ΕΙΣΠΝΟΕΣ"]
        api_rules_dictionary["ΕΝΕΣΗ_ΣΚΟΝΗ_ΦΙΑΛΗ"] = rules_dictionary["ΕΝΕΣΗ"]
        api_rules_dictionary["ΕΝΕΣΗ_ΔΙΑΛ_ΦΥΣΙΓΓΕΣ"] = rules_dictionary["ΕΝΕΣΗ"]
        api_rules_dictionary["ΕΝΕΣΗ_ΔΙΑΛ_ΦΙΑΛΗ"] = rules_dictionary["ΕΝΕΣΗ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΜΑΣΩΜΕΝΑ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΕΝΤΕΡΟΔΙΑΛΥΤΑ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΕΠΙΚΑΛ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΕΠΙΚΑΛΥΜ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΔΙΑΣΠ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΒΡΑΔΕΙΑΣ_ΑΠΟΔΕΣ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΑΝΑΒΡ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΔΙΣΚΙΑ_ΕΛΕΓΧ_ΑΠΟΔ"] = rules_dictionary["ΔΙΣΚΙΑ"]
        api_rules_dictionary["ΕΚΧΥΣΗ_ΔΙΑΛ_ΦΥΣΙΓΓΕΣ"] = rules_dictionary["ΕΚΧΥΣΗ"]
        api_rules_dictionary["ΠΟΣ_ΔΙΑΛΥΜΑ_1ML"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ.ΔΙΑΛ_ΔΟΣΕΙΣ_15ML"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ.ΔΙΑΛ_ΔΟΣΕΙΣ_5ML"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ_ΔΙΑΛΥΜΑ_ML"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ_ML"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ.ΔΙΑΛ_ΔΟΣΕΙΣ"] = rules_dictionary["ΠΟΣ.ΔΙΑΛΥΜΑ"]
        api_rules_dictionary["ΠΟΣ.ΣΚΟΝΗ_ΔΟΣ_ΔΙΑΛΥΜΑ"] = rules_dictionary["ΠΟΣ.ΣΚΟΝΗ"]
        api_rules_dictionary["ΚΑΨΟΥΛΕΣ_ΕΝΤΕΡΟΔΙΑΛ"] = rules_dictionary["ΚΑΨΟΥΛΕΣ"]
        api_rules_dictionary["ΚΑΨΟΥΛΑ_ΕΛΕΓΧΟΜ_ΑΠΟΔΕΣΜ"] = rules_dictionary["ΚΑΨΟΥΛΕΣ"]
        return extract_from_rules(
            description=clear_description,
            rules=api_rules_dictionary[substance_administration.consumable.form_code.translation],
        )
    except KeyError:
        return KEY_ERROR, None
