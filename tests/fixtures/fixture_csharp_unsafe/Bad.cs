using System;
using System.Diagnostics;

namespace Demo
{
    public class Bad
    {
        // TODO: replace Process.Start with explicit ProcessStartInfo
        public unsafe void Run()
        {
            Console.WriteLine("starting");
            var p = Process.Start("cmd.exe", "/c dir");
            try
            {
                int x = 1;
            }
            catch
            {
            }
            dynamic d = 42;
        }
    }
}
