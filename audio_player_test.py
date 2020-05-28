def dummy_audio_producer(audio_queue, end_event, logging):
    i = 0
    while(not end_event.is_set()):
        audio_filenames = ["john_cena.mp3", "megolovania_short.mp3", "screaming_sheep.mp3", "oh_no_no_no.mp3"]
        put_in_queue(audio_queue, audio_filenames[i % 4], end_event)
        logging.info("AP::" + audio_filenames[i % 4] + " produced")
        time.sleep(20)
        i += 1


def audio_player_test(test_duration=30):

    test play_based_on_os
    prev_dir = os.getcwd()
    os.chdir('static')
    os.chdir('audio')

    play_based_on_os('john_cena.mp3')
    play_based_on_os('megolovania_short.mp3')
    os.chdir(prev_dir)

    # test audio player thread
    end_event = threading.Event()
    audio_queue = queue.Queue()
    seconds = 0

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.basicConfig(format=format, level=logging.WARN,
                        datefmt="%H:%M:%S")
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.INFO)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        audio_producer_future = executor.submit(dummy_audio_producer, audio_queue, end_event, logging)
        audio_consumer_future = executor.submit(audio_player, audio_queue, end_event, logging)
        while(seconds < test_duration):
            logging.info("t=" +str(seconds))
            logging.info("APF::" + str(audio_producer_future))
            logging.info("ACF::" + str(audio_consumer_future))
            time.sleep(1)
            seconds += 1

        end_event.set()
        time.sleep(15)  # audio player can't exit (without sigint) until audio file is done being played
        confirm_thread_finished(audio_producer_future)
        confirm_thread_finished(audio_consumer_future)
        print("audio thread test finished")

audio_player_test()
