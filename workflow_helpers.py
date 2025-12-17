# HELPER FUNCTIONS---------------------------------------------------------------------------------
import os
import time
import json 
import logging 
import threading 
import csv 
from datetime import datetime

import cv2 
import paramiko 

# define helper functions to manage solution
def fillWell(
    opentronsClient,
    strLabwareName_from,
    strWellName_from,
    strOffsetStart_from,
    strPipetteName,
    strLabwareName_to,
    strWellName_to,
    strOffsetStart_to,
    intVolume: int,
    fltOffsetX_from: float = 0,
    fltOffsetY_from: float = 0,
    fltOffsetZ_from: float = 0,
    fltOffsetX_to: float = 0,
    fltOffsetY_to: float = 0,
    fltOffsetZ_to: float = 0,
    intMoveSpeed : int = 100, 
    needMixing: bool = False,
) -> None:
    '''
    function to manage solution in a well because the maximum volume the opentrons can move is 1000 uL
    
    Parameters
    ----------
    opentronsClient : opentronsClient
        instance of the opentronsClient class

    strLabwareName_from : str
        name of the labware to aspirate from

    strWellName_from : str
        name of the well to aspirate from

    strOffset_from : str
        offset to aspirate from
        options: 'bottom', 'center', 'top'

    strPipetteName : str
        name of the pipette to use

    strLabwareName_to : str
        name of the labware to dispense to

    strWellName_to : str
        name of the well to dispense to

    strOffset_to : str
        offset to dispense to
        options: 'bottom', 'center', 'top'  

    intVolume : int
        volume to transfer in uL    

    intMoveSpeed : int
        speed to move in mm/s
        default: 100
    '''
    
    # while the volume is greater than 1000 uL
    while intVolume > 1000:
        # move to the well to aspirate from
        opentronsClient.moveToWell(strLabwareName = strLabwareName_from,
                                   strWellName = strWellName_from,
                                   strPipetteName = strPipetteName,
                                   strOffsetStart = 'top',
                                   fltOffsetX = fltOffsetX_from,
                                   fltOffsetY = fltOffsetY_from,
                                   intSpeed = intMoveSpeed)
                                   
        time.sleep(0.01)
        
        # aspirate 1000 uL
        opentronsClient.aspirate(strLabwareName = strLabwareName_from,
                                 strWellName = strWellName_from,
                                 strPipetteName = strPipetteName,
                                 intVolume = 1000,
                                 strOffsetStart = strOffsetStart_from,
                                 fltOffsetX = fltOffsetX_from,
                                 fltOffsetY = fltOffsetY_from,
                                 fltOffsetZ = fltOffsetZ_from)

        time.sleep(0.01)
        
        # move to the well to dispense to
        opentronsClient.moveToWell(strLabwareName = strLabwareName_to,
                                   strWellName = strWellName_to,
                                   strPipetteName = strPipetteName,
                                   strOffsetStart = 'top',
                                   fltOffsetX = fltOffsetX_to,
                                   fltOffsetY = fltOffsetY_to,
                                   intSpeed = intMoveSpeed)

        time.sleep(0.01)
        
        # dispense 1000 uL
        opentronsClient.dispense(strLabwareName = strLabwareName_to,
                                 strWellName = strWellName_to,
                                 strPipetteName = strPipetteName,
                                 intVolume = 1000,
                                 strOffsetStart = strOffsetStart_to,
                                 fltOffsetX = fltOffsetX_to,
                                 fltOffsetY = fltOffsetY_to,
                                 fltOffsetZ = fltOffsetZ_to)

        time.sleep(0.01)
        
        opentronsClient.blowout(strLabwareName = strLabwareName_to,
                                strWellName = strWellName_to,
                                strPipetteName = strPipetteName,
                                strOffsetStart = strOffsetStart_to,
                                fltOffsetX = fltOffsetX_to,
                                fltOffsetY = fltOffsetY_to,
                                fltOffsetZ = fltOffsetZ_to)

        time.sleep(0.01)
        
        # subtract 1000 uL from the volume
        intVolume -= 1000
    
        # move to the well to aspirate from
    opentronsClient.moveToWell(strLabwareName = strLabwareName_from,
                               strWellName = strWellName_from,
                               strPipetteName = strPipetteName,
                               strOffsetStart = 'top',
                               fltOffsetX = fltOffsetX_from,
                               fltOffsetY = fltOffsetY_from,
                               intSpeed = intMoveSpeed)
    
    # aspirate the remaining volume
    opentronsClient.aspirate(strLabwareName = strLabwareName_from,
                             strWellName = strWellName_from,
                             strPipetteName = strPipetteName,
                             intVolume = intVolume,
                             strOffsetStart = strOffsetStart_from,
                             fltOffsetX = fltOffsetX_from,
                             fltOffsetY = fltOffsetY_from,
                             fltOffsetZ = fltOffsetZ_from)
    
    # move to the well to dispense to
    opentronsClient.moveToWell(strLabwareName = strLabwareName_to,
                               strWellName = strWellName_to,
                               strPipetteName = strPipetteName,
                               strOffsetStart = 'top',
                               fltOffsetX = fltOffsetX_to,
                               fltOffsetY = fltOffsetY_to,
                               intSpeed = intMoveSpeed)
    
    # dispense the remaining volume
    opentronsClient.dispense(strLabwareName = strLabwareName_to,
                             strWellName = strWellName_to,
                             strPipetteName = strPipetteName,
                             intVolume = intVolume,
                             strOffsetStart = strOffsetStart_to,
                             fltOffsetX = fltOffsetX_to,
                             fltOffsetY = fltOffsetY_to,
                             fltOffsetZ = fltOffsetZ_to)
    
    # blowout
    opentronsClient.blowout(strLabwareName = strLabwareName_to,
                            strWellName = strWellName_to,
                            strPipetteName = strPipetteName,
                            strOffsetStart = strOffsetStart_to,
                            fltOffsetX = fltOffsetX_to,
                            fltOffsetY = fltOffsetY_to,
                            fltOffsetZ = fltOffsetZ_to)
    
    if needMixing: 
        for i in range(6):
            print("mixing cycle: ", i+1)
            opentronsClient.aspirate(strLabwareName = strLabwareName_to,
                                strWellName = strWellName_to,
                                strPipetteName = strPipetteName,
                                intVolume = 1000,
                                strOffsetStart = strOffsetStart_to,
                                fltOffsetX = fltOffsetX_to,
                                fltOffsetY = fltOffsetY_to,
                                fltOffsetZ = -30)
                            
            time.sleep(0.01)

            opentronsClient.dispense(strLabwareName = strLabwareName_to,
                                strWellName = strWellName_to,
                                strPipetteName = strPipetteName,
                                intVolume = 1000,
                                strOffsetStart = strOffsetStart_to,
                                fltOffsetX = fltOffsetX_to,
                                fltOffsetY = fltOffsetY_to,
                                fltOffsetZ = -30)
        
    return


# define helper function to wash reactor
def washReactor(oc,
                strID_NISreactor,
                strWell2Test,
                strID_electrodeTipRack,
                well_path,
                pumps,
                prePictureName = None, 
                postPictureName = None,
                type='NIS'
                ):
    '''
    function to wash reactor

    Parameters
    ----------
    opentronsClient : opentronsClient
        instance of the opentronsClient class

    strLabwareName : str
        name of the labware to wash electrode in

    intCycle : int
        number of cycles to wash electrode

    '''

    # rinse cycle 4 times: nozzle immerse 3 times
    # pick up nozzle 
    oc.moveToWell(
            strLabwareName=strID_electrodeTipRack,
            strWellName='B1',
            strPipetteName="p1000_single_gen2",
            strOffsetStart='top',
            fltOffsetX=0.5,
            fltOffsetY=0.5,
            fltOffsetZ=2,
            intSpeed=50
        )

    time.sleep(0.01)

    oc.pickUpTip(
            strLabwareName=strID_electrodeTipRack,
            strWellName='B1',
            strPipetteName="p1000_single_gen2",
            strOffsetStart='top',
            fltOffsetX=0.5,
            fltOffsetY=0.5
        )

    time.sleep(0.01)

    if type == 'NIS':
        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2',
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-35,
                intSpeed=50
            )

        time.sleep(0.01)

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2',
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-40,
                intSpeed=50
            )

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2', 
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-50,
                intSpeed=50
            )

        time.sleep(0.01)

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

    elif type == 'Yang':
        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2',
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-30,
                intSpeed=50
            )

        time.sleep(0.01)

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2',
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-40,
                intSpeed=50
            )

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2', 
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                fltOffsetZ=-54,
                intSpeed=50
            )

        time.sleep(0.01)

        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

    if prePictureName is not None:
        # put nozzle back to tip rack
        oc.moveToWell(
                strLabwareName=strID_electrodeTipRack,
                strWellName='B1',
                strPipetteName="p1000_single_gen2",
                strOffsetStart='top',
                fltOffsetX=0.5,
                fltOffsetY=0.5,
                fltOffsetZ=2,
                intSpeed=50
            )

        time.sleep(0.01)

        oc.dropTip(
                strLabwareName=strID_electrodeTipRack,
                boolDropInDisposal=False,
                strWellName='B1',
                strPipetteName="p1000_single_gen2",
                strOffsetStart='top',
                fltOffsetX=0.5,
                fltOffsetY=0.5,
                fltOffsetZ=-88
            )
        
        time.sleep(0.01)
        
        oc.moveToWell(
            strLabwareName=strID_electrodeTipRack,
            strWellName='B1',
            strPipetteName="p1000_single_gen2",
            strOffsetStart='top',
            fltOffsetX=0.5,
            fltOffsetY=0.5,
            fltOffsetZ=20,
            intSpeed=50
        )

        time.sleep(0.01)

        take_picture(oc, strID_NISreactor, strWell2Test, prePictureName, well_path)
        logging.info("Taken pre-wash picture.")

        time.sleep(0.01)

        # pick up nozzle 
        oc.moveToWell(
                strLabwareName=strID_electrodeTipRack,
                strWellName='B1',
                strPipetteName="p1000_single_gen2",
                strOffsetStart='top',
                fltOffsetX=0.5,
                fltOffsetY=0.5,
                fltOffsetZ=2,
                intSpeed=50
            )

        time.sleep(0.01)

        oc.pickUpTip(
                strLabwareName=strID_electrodeTipRack,
                strWellName='B1',
                strPipetteName="p1000_single_gen2",
                strOffsetStart='top',
                fltOffsetX=0.5,
                fltOffsetY=0.5
            )

        time.sleep(0.01)

        oc.moveToWell(
                strLabwareName=strID_NISreactor,
                strWellName=strWell2Test,
                strPipetteName='p1000_single_gen2', 
                strOffsetStart='top',
                fltOffsetX=0.3,
                fltOffsetY=0.5,
                # fltOffsetZ=-54,
                fltOffsetZ=-50,
                intSpeed=50
            )

        time.sleep(0.01)

    for i in range(4):
        pumps.on(2, 2000)  # add H2O for 2 s (auto-off)
        time.sleep(3)
        pumps.on(3, 10000)  # out for 10 s (auto-off)
        time.sleep(11)

    # put nozzle back to tip rack
    oc.moveToWell(
            strLabwareName=strID_electrodeTipRack,
            strWellName='B1',
            strPipetteName="p1000_single_gen2",
            strOffsetStart='top',
            fltOffsetX=0.5,
            fltOffsetY=0.5,
            fltOffsetZ=2,
            intSpeed=50
        )

    time.sleep(0.01)

    oc.dropTip(
            strLabwareName=strID_electrodeTipRack,
            boolDropInDisposal=False,
            strWellName='B1',
            strPipetteName="p1000_single_gen2",
            strOffsetStart='top',
            fltOffsetX=0.5,
            fltOffsetY=0.5,
            fltOffsetZ=-88
        )
    
    time.sleep(0.01)

    oc.moveToWell(
        strLabwareName=strID_electrodeTipRack,
        strWellName='B1',
        strPipetteName="p1000_single_gen2",
        strOffsetStart='top',
        fltOffsetX=0.5,
        fltOffsetY=0.5,
        fltOffsetZ=20,
        intSpeed=50
    )

    time.sleep(0.01)

    if postPictureName is not None:
        take_picture(oc, strID_NISreactor, strWell2Test, postPictureName, well_path)
        logging.info("Taken post-wash picture.")

    logging.info("Finished washing reactor in well %s.", strWell2Test)
    return

import time

def washTip(
    oc,
    ultra,
    strID_bath,
    pipette_name="p1000_single_gen2",
    offset_x=0.0,
    offset_y=0.0,
    z_top=10.0,
    z_deep=-30.0,
    offset_start_deep="top",      # 'top' for pH probe, 'bottom' for electrode
    sonicator_channel=2,
    sonication_ms=15000,
    move_speed=100,
):
    """
    Generic wash routine:
    #   1) Water bath (A1)
      2) Acid bath  (A2)
      3) Water bath (A1)
    Each step:
      - move above bath
      - move down into bath
      - sonicate
      - move back up
    """

    def _wash_in_well(well_name: str):
        # Move above bath
        oc.moveToWell(
            strLabwareName=strID_bath,
            strWellName=well_name,
            strPipetteName=pipette_name,
            strOffsetStart="top",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=z_top,
            intSpeed=move_speed,
        )
        time.sleep(0.01)

        # Move down into bath
        oc.moveToWell(
            strLabwareName=strID_bath,
            strWellName=well_name,
            strPipetteName=pipette_name,
            strOffsetStart=offset_start_deep,
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=z_deep,
            intSpeed=move_speed,
        )
        time.sleep(1)

        # Sonicate
        ultra.on(sonicator_channel, sonication_ms)
        # sonication_ms is in ms; wait a bit longer than the sonication
        time.sleep(sonication_ms / 1000.0 + 1)

        # Move back above bath
        oc.moveToWell(
            strLabwareName=strID_bath,
            strWellName=well_name,
            strPipetteName=pipette_name,
            strOffsetStart="top",
            fltOffsetX=offset_x,
            fltOffsetY=offset_y,
            fltOffsetZ=z_top,
            intSpeed=move_speed,
        )
        time.sleep(0.01)

    # ----------------- sequence: water (A1) → acid (A2) → water (A1) -----------------
    # _wash_in_well("A1")  # water
    _wash_in_well("A2")  # acid
    _wash_in_well("A1")  # water


def take_picture(oc, strID_NISreactor, strWellName, imageName, well_dir): 
    oc.moveToWell(strLabwareName = strID_NISreactor,
                strWellName = strWellName,
                strPipetteName = 'p1000_single_gen2',
                strOffsetStart = 'top',
                fltOffsetX = 19.0,
                fltOffsetY = 77.0,
                fltOffsetZ = 50,
                intSpeed = 50)
    time.sleep(3)  # wait for 2 seconds to stabilize
    oc.lights(False)

    # === CONFIGURATION ===
    hostname = '192.168.0.108'

    # hostname = '100.66.74.87'  # ⬅️ Replace this with your Raspberry Pi's real IP address
    username = 'ot2-pi'
    password = '1144'
    remote_image_path = '/home/ot2-pi/remote_image.jpg'
    local_image_path = 'remote_image.jpg'

    # === CONNECT TO PI OVER SSH ===
    print(f"[+] Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    print("[+] SSH connection established.")

    # === RUN REMOTE CAMERA SCRIPT ===
    command = (
        "python3 -c \""
        "from picamera2 import Picamera2; import time; "
        "picam2 = Picamera2(); "
        "config=picam2.create_still_configuration(main={'size': (2028, 1520)}); "
        "picam2.configure(config); "
        "picam2.set_controls({'AwbEnable': True}); "
        "picam2.start(); "
        "time.sleep(2); "
        f"picam2.capture_file('{remote_image_path}'); "
        "picam2.close(); "
        "print('Image captured');"
        "\""
    )

    print("[+] Capturing image on the Pi...")
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout_output = stdout.read().decode()
    stderr_output = stderr.read().decode()

    local_image_path = os.path.join(well_dir, imageName)

    if stderr_output:
        print("[-] Error during image capture:")
        print(stderr_output)
    else:
        print("[+] Remote output:")
        print(stdout_output)

    # === DOWNLOAD IMAGE FROM PI ===
    print("[+] Downloading image to laptop...")
    sftp = ssh.open_sftp()
    sftp.get(remote_image_path, local_image_path)
    sftp.close()
    ssh.close()
    print(f"[+] Image downloaded to {local_image_path}")
    oc.lights(True)


def getPipetteTipLocById(intId) -> str:
    if intId > 96 or intId < 1:
        raise Exception("Pipette id out of range.")
    return chr(ord('A') + ((intId - 1) // 12)) + str((intId - 1) % 12 + 1)

def allocate_from_sources(sources_by_plate: dict, solution_name:str, required_uL: int):
    """
    Search through 'sources_by_plate', which is a dict of dicts mapping well names to remaining uL,
    mutates sources_by_plate[*][*]['remaining_uL']
    returns plan = [(plate_id, well_name, uL_to_take), ...] 
    """
    plan = []
    need = required_uL
    
    for plate_id, wells in sources_by_plate.items():
        for well_name, info in wells.items():
            if info.get("solution") != solution_name:
                continue

            remain = info.get("remaining_uL", 0)
            if remain <= 0 or need <= 0:
                continue

            take = min(remain, need)
            info['remaining_uL'] = remain - take  # mutate remaining amount
            plan.append( (plate_id, well_name, take) )
            need -= take

            if need <= 0:
                break
        if need <= 0:
                break
        
    if need > 0:
        raise Exception(f"Not enough {solution_name} available to allocate {required_uL} uL.")

    return plan 

def fillWell_autoSource(
    opentronsClient,
    sources_by_plate: dict,
    solution_name: str,
    strPipetteName: str,
    strLabwareName_to: str,
    strWellName_to: str,
    strOffsetStart_from: str = "bottom",
    strOffsetStart_to: str = "bottom",
    totalVolume_uL: int = 0,
    fltOffsetX_from: float = 0,
    fltOffsetY_from: float = 0,
    fltOffsetZ_from: float = 0,
    fltOffsetX_to: float = 0,
    fltOffsetY_to: float = 0,
    fltOffsetZ_to: float = 0,
    intMoveSpeed: int = 100,
    needMixing: bool = False,
    experimentName: str = None,
    strMetadataPath: str = None,
):
    """
    Auto-pick source wells and reduce their remaining amounts while transferring 'totalVolume_uL'
    into (strLabwareName_to, strWellName_to) using your existing fillWell().
    """
    plan = allocate_from_sources(sources_by_plate, solution_name, totalVolume_uL)  # mutates sources_by_plate
    for plate_id, well_from, vol_uL in plan:
        experimentData = {
            "solution_name": solution_name,
            "source_plate": plate_id,
            "source_well": well_from,
            "volume_uL": vol_uL,
        }
        if experimentName is not None:
            record_experiment_data(strMetadataPath, experimentName, "solutionAdded", experimentData)
        
        logging.info(f"Transferring {vol_uL} uL from {plate_id} {well_from} to {strLabwareName_to} {strWellName_to}")
        fillWell(
            opentronsClient=opentronsClient,
            strLabwareName_from=plate_id,
            strWellName_from=well_from,
            strOffsetStart_from=strOffsetStart_from,
            strPipetteName=strPipetteName,
            strLabwareName_to=strLabwareName_to,
            strWellName_to=strWellName_to,
            strOffsetStart_to=strOffsetStart_to,
            intVolume=vol_uL,
            fltOffsetX_from=fltOffsetX_from,
            fltOffsetY_from=fltOffsetY_from,
            fltOffsetZ_from=fltOffsetZ_from,
            fltOffsetX_to=fltOffsetX_to,
            fltOffsetY_to=fltOffsetY_to,
            fltOffsetZ_to=fltOffsetZ_to,
            intMoveSpeed=intMoveSpeed,
            needMixing=needMixing,
        )

def getWellName(index: int) -> str:
    if not (1 <= index <= 15):
        raise ValueError("Index out of range (1-15)")

    rows = ["A", "B", "C"]
    num_rows = 3

    # column-major ordering:
    row_index = (index - 1) % num_rows
    col_index = (index - 1) // num_rows + 1

    return f"{rows[row_index]}{col_index}"

def wellNameToIndex(wellName: str) -> int:
    wellName = wellName.strip().upper()
    row = ord(wellName[0]) - ord('A')
    col = int(wellName[1:]) - 1
    return row * 5 + col + 1

class VideoRecorder:
    def __init__(self, camera_index=0, width=1280, height=720, fps=30, out_path="experiment.mp4"):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.out_path = out_path

        self.cap = None
        self.out = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            print("Camera is already running.")
            return

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.out_path, fourcc, self.fps, (self.width, self.height))
        self.running = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

        logging.info(f"Video recording started -> {self.out_path}")

    def _record_loop(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                logging.error("Failed to read frame from camera")
                continue
            self.out.write(frame)
            time.sleep(1 / self.fps)

    def stop(self):
        """Stop the video recording."""
        if not self.running:
            print("Camera is not running.")
            return
        self.running = False
        self.thread.join()
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        logging.info(f"Video recording stopped -> {self.out_path}")

VALID_WELLS = {f"{row}{col}" for row in ["A", "B", "C"] for col in range(1, 6)}

def load_experiment_csv(path):
    wells = []
    errors = []
    seen_wells = set()

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        line_num = 1

        for row in reader:
            line_num += 1

            raw_name = (row.get("wellName") or "").strip()
            if not raw_name:
                continue
            well_name = raw_name.upper()

            if well_name not in VALID_WELLS:
                errors.append(f"Line {line_num}: Invalid well name '{well_name}'. Allowed: A1-C5.")
                continue

            if well_name in seen_wells:
                errors.append(f"Line {line_num}: Duplicate well name '{well_name}'.")
                continue
            seen_wells.add(well_name)

            try: 
                well_id = int(row["well ID"])
            except: 
                well_id = None
                errors.append(f"Line {line_num}: Invalid well ID '{row.get('well ID')}'.")

            def parse_float(field, name):
                val_str = (row.get(field) or "").strip()
                if not val_str:
                    return None
                try:
                    return float(val_str)
                except:
                    errors.append(f"Line {line_num}: Invalid float value '{val_str}' in '{name}'.")
                    return None

            temperature_C = parse_float("temperature_C", "temperature_C")
            depositionCurrent_mA = parse_float("depositionCurrent_mA", "depositionCurrent_mA")
            depositionTime_s = parse_float("depositionTime_s", "depositionTime_s")
            
            well = {
                "well_id": well_id,
                "well_name": well_name,
                "temperature_C": temperature_C,
                "depositionCurrent_mA": depositionCurrent_mA,
                "depositionTime_s": depositionTime_s,
                "solutions": []
            }

            for label in ["A", "B", "C", "D"]:
                name_key = f"solution {label} name"
                volume_key = f"solution {label} volume_mL"

                name = (row.get(name_key) or "").strip()
                vol_raw = (row.get(volume_key) or "").strip()

                if not name and not vol_raw:
                    continue  # skip empty solution

                if not name: 
                    errors.append(f"Line {line_num}: Missing name for solution {label}.")
                    continue

                if not vol_raw:
                    errors.append(f"Line {line_num}: Missing volume for solution {label}.")
                    continue

                try: 
                    volume_mL = float(vol_raw)
                    if volume_mL <= 0:
                        raise ValueError("Volume must be positive.")
                except:
                    errors.append(f"Line {line_num}: Invalid volume '{vol_raw}' for solution {label}.")
                    continue

                solution = {
                    "label": label,
                    "name": name,
                    "volume_mL": volume_mL
                }

                well["solutions"].append(solution)

            wells.append(well)

    return wells, errors 



# LOGGING------------------------------------------------------------------------------------

def record_event(strMetadataPath: str, name: str, temp: float | None = None):
    if os.path.exists(strMetadataPath):
        with open(strMetadataPath, 'r') as f:
            meta = json.load(f)

    else: 
        meta = {}
    
    events = meta.get("events", {})

    entry = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if temp is not None:
        entry["temp_C"] = temp
    events[name] = entry

    meta["events"] = events
    with open(strMetadataPath, 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logging.info(f"Recorded event '{name}' in metadata.")

def record_ph_series(strMetadataPath: str, series):
    """
    Store the pH time series into metadata as a list of 
    {"time": timestamp, "pH": value}
    """ 
    if os.path.exists(strMetadataPath):
        with open(strMetadataPath, 'r') as f:
            meta = json.load(f)
    else: 
        meta = {}

    ph_list = []
    for ts, val in series:
        ph_list.append({"timestamp": ts, "pH": val})

    meta["pH_series"] = ph_list
    with open(strMetadataPath, 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logging.info(f"Recorded %d pH points in metadata.", len(series))

def record_experiment_data(
    strMetadataPath: str,
    section: str,
    key: str,
    value,
):
    """
    Record a key-value pair into experimentData[section][key].

    - For most keys: overwrite experimentData[section][key] with `value`
    - For key == "solutionAdded": store a *list* and append new entries
    - Automatically converts tuples like ('A1', 10) into dicts: {"well": "A1", "uL": 10}
    - Handles lists (e.g. from allocate_from_sources) by converting each element.
    """

    # Load metadata or create new one
    if os.path.exists(strMetadataPath):
        with open(strMetadataPath, 'r') as f:
            meta = json.load(f)
    else:
        meta = {}

    # Ensure base structure
    experimentData = meta.get("experimentData", {})
    experimentData.setdefault("deposition", {})
    experimentData.setdefault("characterization", {})

    # Validate section
    if section not in experimentData:
        raise ValueError(
            f"Unknown section '{section}'. Must be 'deposition' or 'characterization'."
        )

    # Helper: convert tuples to dicts (for readability)
    def convert(item):
        if isinstance(item, tuple) and len(item) == 2:
            well, amount = item
            return {"well": well, "uL": amount}
        return item

    # Normalize value (apply convert)
    if isinstance(value, list):
        value = [convert(v) for v in value]
    else:
        value = convert(value)

    # Special behavior for solutionAdded: treat as an *append-to-list* field
    if key == "solutionAdded":
        current = experimentData[section].get(key)

        # If no previous solutionAdded → start a new list
        if current is None:
            experimentData[section][key] = []
        # If somehow something else was stored there → wrap it into a list
        elif not isinstance(current, list):
            experimentData[section][key] = [current]

        # Now experimentData[section][key] is guaranteed to be a list
        if isinstance(value, list):
            experimentData[section][key].extend(value)
        else:
            experimentData[section][key].append(value)
    else:
        # Default behavior: just overwrite
        experimentData[section][key] = value

    # Save back
    meta["experimentData"] = experimentData
    with open(strMetadataPath, 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logging.info(f"Recorded {section}.{key} in metadata.")
