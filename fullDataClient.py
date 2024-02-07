from exchange.video import ScreenShareClient
from exchange.video import StreamingServer
from exchange.audio import AudioReceiver
from exchange.audio import AudioSender
from exchange.streaming import Service
from ipUtils import OperationOutcome

import queue
import time
import threading


# ip_address = where the server is running, usually remote
# client here means stream producer
def run_full_client(ip_address: str):
    # noinspection PyTypeChecker
    client = None
    attempt = 1
    next_command: OperationOutcome = OperationOutcome.STANDBY
    while next_command is not OperationOutcome.EXIT:
        if attempt > 1:
            print(f"Attempt number {attempt}. Waiting {2 ** attempt} seconds before next retry...")
            time.sleep(2 ** (attempt - 1))
        try:
            client: tuple[ScreenShareClient, AudioSender] = client_connect(ip_address)
            next_command = interrupt_wait_as_daemon(client)
            attempt += 1
        except Exception as e:
            print(f"Operation failed with error: {e}. Retrying...")
            if next_command is OperationOutcome.EXIT:
                print("Exiting...")
            else:
                print("Retrying...")

        finally:
            # stop all active clients, before exit or retry
            if client is not None:
                for item in client:
                    if item is not None:
                        item.stop_stream()
                        class_name = item.__class__.__name__
                        print(f"Client {class_name} has just stopped")


def client_connect(ip_address: str) -> tuple[ScreenShareClient, AudioSender]:
    video_sender = ScreenShareClient(ip_address, 9999, x_res=1920, y_res=1080)
    tv = threading.Thread(target=video_sender.start_stream)
    tv.daemon = True
    tv.start()

    audio_sender = AudioSender(ip_address, 9998)
    ta = threading.Thread(target=audio_sender.start_stream)
    ta.daemon = True
    ta.start()

    return video_sender, audio_sender


# ip_address = where to run the server, usually localhost ip
# server here means stream receiver
def run_full_server(ip_address: str):
    server = None
    next_command: OperationOutcome = OperationOutcome.STANDBY
    while next_command is not OperationOutcome.EXIT:
        try:
            server: tuple[Service, Service] = server_connect(ip_address)
            next_command = interrupt_wait_as_daemon(server)
        except Exception as e:
            print(f"Operation failed with error: {e}.")
            if next_command is OperationOutcome.EXIT:
                print("Exiting...")
            else:
                print("Retrying...")

        finally:
            if server is not None:
                for item in server:
                    if item is not None:
                        item.stop_server()


def server_connect(ip_address: str) -> tuple[Service, Service]:
    video_receiver = StreamingServer(ip_address, 9999)
    tv = threading.Thread(target=video_receiver.start_server())
    tv.daemon = True
    tv.start()

    audio_receiver = AudioReceiver(ip_address, 9998)
    ta = threading.Thread(target=audio_receiver.start_server())
    ta.daemon = True
    ta.start()

    return video_receiver, audio_receiver


# checking user input + verifying the issue on the client side
def interrupt_wait_as_daemon(client: tuple[Service, Service]):
    operational_input_queue = queue.Queue()
    input_thread = threading.Thread(target=collect_user_input, args=(operational_input_queue,))
    input_thread.daemon = True  # Optional: Makes the thread exit when the main program exits
    input_thread.start()

    highest_order_command: OperationOutcome = OperationOutcome.STANDBY

    while highest_order_command == OperationOutcome.STANDBY:
        # Check if the queue has been populated
        check_client_exception_queue(client, operational_input_queue)
        while not operational_input_queue.empty():
            command = operational_input_queue.get()
            if highest_order_command.value < command.value:
                highest_order_command = command
        time.sleep(0.5)

    print(f'Executing command: {highest_order_command.name}')
    return highest_order_command


def check_client_exception_queue(client: tuple[Service, Service], operational_input_queue: queue.Queue):
    for element in client:
        if hasattr(element, "get_exceptions"):
            while element.has_exceptions():
                current_exception = element.get_exceptions().get()
                class_name = element.__class__.__name__
                print(f'Caught an exception in client.{class_name}: {current_exception}')
                operational_input_queue.put(OperationOutcome.RETRY)
                element.get_exceptions().task_done()


def collect_user_input(operational_input_queue: queue.Queue):
    try:
        while True:
            user_input = input("Enter 'q' or 'АСТАНАВІТЕСЬ' to exit OR 'r' for restart: ").lower()
            if user_input == 'r':
                operational_input_queue.put(OperationOutcome.RETRY)
                break
            elif user_input in ['астанавітесь', 'q']:
                operational_input_queue.put(OperationOutcome.EXIT)
                break
    except Exception as e:
        print(f"Operation failed with error: {e}. Stopping...")
        operational_input_queue.put(OperationOutcome.FAILURE)


ASTANAVITES = """
                                                                                                    
                                                                                                    
                                                                                                    
                                  ####%%%%%%%#######%%%#####                                        
                              ***#####%%%%%%%#######%%%%########*                                   
                           ##**#############%%%%%####%%%%%%%%########                               
                        %#######################%%%%%%%%%%%%%%%%%#####                              
                     #################%%%%%%%%%%%%%%%%%%%%%%%%%%%%%######                           
                   **###############%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##*#                         
                  **###############%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%###*                        
                ***#############%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%##*                       
               ***############%%%###%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%###**                     
               **############%%%%####%%%%%%%%%%%%%%%%%%%#############%%###%%##**                    
              **#####################%%%%%%%%%%%%%%%%###********#####%%#######***                   
             **#######################%%%%%%%%%#####****++++++++*****##%######****                  
             *#################################*****+++++===++++++++**#########****                 
             ##%%########*****###************+++++==============+++++***########*++                 
            ##%######*********++++++++==========================++++++***########*++                
            ########*++++++++===================================++++++****########+++               
            #%####**+++==========================-===============++++++***####***#*++               
            ####**++==============================================+++++***#####****+=               
            ###**++=====--------=====================================+++***#####**++==              
            ###**++===------------====--==============================+++***####***+==              
            ##***++===-------------===================================+++++**####**+==              
           ##****++===-------------=================================++++++++****#**+==              
           ##***+++===-----------============---=====================+++++++****#***+=              
           #*****++===-------------===---===-------=========+*##+===+++++++++***##*+==              
           #******+====---------------------------=======+*%@@*++++++++++++++***##*+==              
            ***#**+=====---------======---------=====+%@@@%*+++++++++++=++++++**#**+==              
            ***#**+======-=+#**+===================+*@@#*===++++++++++===+++++***++===              
            **##**+========+++*#%@@@@@%#+====-====+*%*+**##*#+**##**+=====++++***++===              
             *###**================+++**##+==--==++**+**=:+##*++++++=========++++*+===              
              *###*============+*#*##**#**+=----==+++=======++====+=============+#*+=               
               *##*+========+##++####*+++===----==++=============+==============+#*+=               
               +***+=======+*+==+**+========----===============================++**==               
                 ***====================--------==============================+++*+==               
                  +++==---============---------==========-================+===++++==                
                  +====-------===---=--===----=====++++++================+++++++++==                
                   =====-------------==+*+==---====+++++#+++============+++++++++==                 
                    -====----------==+*#===------===+++++#*+++==========+++++++++==                 
                    =======----====++##+======--===+++*+**++++++========+++++++++==                 
                     -============++#*+=+#%#++++++*##*++++==+++++======+++++++++==-                 
                     +===========+++*+==========+**++++++==============+++++++++==                  
                       ==========++++===================================++++++++==                  
                        ========+++++==------===========+++++===========++++++++=                   
                        +=======++++======+***********+=****++==========+++++++++                   
                        ++======++++====+*#*-.:. ......:==*#**++========++++++++++                  
                        +++===========++****===--=+++**++++=============+++++++%@@%@                
                         +++=================++++++++++================++++++++#@@@@@#=             
                          *+==========================================++++++++--=%@@@@%*            
                           *+=====================+++++*+============++++++++-:---#%@@%%#+          
                           #=====================+*****+=========+++++++++++=:----=#%@%%%#=:-       
                           %-=++++==+===========================++++++++++++-----==*%%%%%%@*---     
                          %%+:=+++++==============---==========++++++++++++-:----=+*%@%%%%%%#=---   
                     %%%%%%%%:-=+++++============---==========+++*****+**+-------=+*%@%%%%%%%%#---- 
                 %%%%%%%%%%%@:.-=++++++===================+++++*#*******+--------=+#@@%%%%%%%%%%%+=-
              %%%%%%%%%%%%%%%=:.:-=++++++==========++++++++**##*******+=-------::+#%@%%%%@%%%%%%%%%%
           %%%%%%%%%%%%%%%%%%+:...:-==+++++++++*********************+=---:::--::-*%%%%%%%%%%%%%%%%%%
       %%%%%%%%%%%%%%%%%%%%%%*:.....:-====++++++******************=---::::::::::=%%%%%%@@@@@%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*:........:-===++++***###********+=--:::::::::::::-#%%%%%%@@@@@%%%%%%%@
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*::..........-====+*********+++=-::......:::::::::*%%%%%%%@@@@@%%%%%@@@
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*::.............-==+****++++-:...........::::::::*%%%%%%%%@@@@@%%%%%@@@
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*:::...............:-====-:...............::::.:+@%%%%%%%%@@@@@%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*::...............:=:::-=-.................::::=@%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#::::..........:=%%%%%####*+-...............::=@%%%%%%%%%%%%%%%%%%%%%%%
"""
