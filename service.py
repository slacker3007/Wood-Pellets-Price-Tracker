import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import schedule
import time
import traceback

class ScraperService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WoodPelletsScraperService'
    _svc_display_name_ = 'Wood Pellets Scraper Service'
    _svc_description_ = 'Runs the wood pellets price scraper daily at 13:00.'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # And set the event.
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # This is the main execution block
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        # Make sure working directory is the script directory
        current_dir = os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))
        os.chdir(current_dir)

        # Ensure the directory is in sys.path so we can import scraper
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        def job():
            try:
                import scraper
                # Execute the main function of the scraper
                scraper.main()
            except Exception as e:
                # Log the error if the scraper fails
                with open(os.path.join(current_dir, "service_error.log"), "a") as f:
                    f.write(f"\\nError running job at {time.strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}\\n")
                    f.write(traceback.format_exc())

        # Schedule the job to run every day at 13:00
        schedule.every().day.at("13:00").do(job)

        while True:
            # Check if a stop signal was received
            # We wait 5 seconds at a time
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal received, break out of the loop
                break
            
            # Check for scheduled tasks
            schedule.run_pending()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ScraperService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ScraperService)
