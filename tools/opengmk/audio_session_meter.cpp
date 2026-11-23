// Read-only per-process Core Audio meter. Does not record audio or change volume.
#include <windows.h>
#include <mmdeviceapi.h>
#include <audiopolicy.h>
#include <endpointvolume.h>
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 3) return 2;
    const DWORD wanted = strtoul(argv[1], nullptr, 10);
    const int samples = atoi(argv[2]) * 10;
    if (!wanted || samples <= 0 || samples > 6000) return 2;
    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) return 3;
    IMMDeviceEnumerator* enumerator = nullptr;
    hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL,
                          __uuidof(IMMDeviceEnumerator), (void**)&enumerator);
    if (FAILED(hr)) { CoUninitialize(); return 4; }
    IMMDeviceCollection* devices = nullptr;
    hr = enumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &devices);
    std::vector<IAudioMeterInformation*> meters;
    if (SUCCEEDED(hr)) {
        UINT count = 0; devices->GetCount(&count);
        for (UINT d = 0; d < count; ++d) {
            IMMDevice* device = nullptr;
            IAudioSessionManager2* manager = nullptr;
            IAudioSessionEnumerator* sessions = nullptr;
            if (SUCCEEDED(devices->Item(d, &device)) &&
                SUCCEEDED(device->Activate(__uuidof(IAudioSessionManager2), CLSCTX_ALL,
                                          nullptr, (void**)&manager)) &&
                SUCCEEDED(manager->GetSessionEnumerator(&sessions))) {
                int n = 0; sessions->GetCount(&n);
                for (int s = 0; s < n; ++s) {
                    IAudioSessionControl* control = nullptr;
                    IAudioSessionControl2* detail = nullptr;
                    if (SUCCEEDED(sessions->GetSession(s, &control)) &&
                        SUCCEEDED(control->QueryInterface(__uuidof(IAudioSessionControl2), (void**)&detail))) {
                        DWORD pid = 0; detail->GetProcessId(&pid);
                        if (pid == wanted) {
                            IAudioMeterInformation* meter = nullptr;
                            if (SUCCEEDED(control->QueryInterface(__uuidof(IAudioMeterInformation), (void**)&meter)))
                                meters.push_back(meter);
                        }
                    }
                    if (detail) detail->Release();
                    if (control) control->Release();
                }
            }
            if (sessions) sessions->Release();
            if (manager) manager->Release();
            if (device) device->Release();
        }
        devices->Release();
    }
    printf("{\"pid\":%lu,\"matching_session_meters\":%zu}\n", wanted, meters.size());
    for (int sample = 0; sample < samples && !meters.empty(); ++sample) {
        float peak = 0;
        for (auto* meter : meters) {
            float value = 0;
            if (SUCCEEDED(meter->GetPeakValue(&value)) && value > peak) peak = value;
        }
        printf("{\"elapsed_s\":%.1f,\"peak\":%.9f}\n", sample / 10.0, peak);
        fflush(stdout);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    for (auto* meter : meters) meter->Release();
    enumerator->Release();
    CoUninitialize();
    return meters.empty() ? 5 : 0;
}
