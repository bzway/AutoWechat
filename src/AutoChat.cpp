#include <stdio.h>
#include <windows.h>
#include <shellapi.h>
#include <process.h>

int main(int argc, char **argv)
{
    //char buf[80];
    //getcwd(buf, sizeof(buf));
    if  (argc>0)
    {
        HWND hwnd=GetForegroundWindow();//直接获得前景窗口的句柄  
        ShowWindow(hwnd,0); 
    }
    system("DLLS\\Python.exe WebBrowser.py");    
}