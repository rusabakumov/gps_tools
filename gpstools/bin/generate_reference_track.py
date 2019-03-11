#!/usr/local/bin/python3
# def parse_args(argv):
#     try:
#         opts, args = getopt.getopt(argv, "hp:", ["path="])
#     except getopt.GetoptError:
#         print('track_stats.py -p <path>')
#         sys.exit(2)
#     for opt, arg in opts:
#         if opt == '-h':
#             print('track_stats.py -p <path>')
#             sys.exit()
#         elif opt in ("-p", "--path"):
#             return arg
#
#
# if __name__ == "__main__":
#     path = parse_args(sys.argv[1:])
#     print("Processing path %s" % path)
#     tracks = load_tracks(path)
#
#     # Prompt to continue
#
#     #cropped_tracks = find_common_activity_segments(tracks)
#
#     # Prompt to select reference
#
#     #print_tracks_stats(cropped_tracks)
#
#     # Prompt to select finish point
#
