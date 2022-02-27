#ifndef HELPER_HPP
#define HELPER_HPP

#include <string>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <algorithm>

/***************************************************************************************************/

class Helper
{
public:
    static const std::string cpu_model();
    static const std::string cpu_freq();
    static const std::string cpu_temp();
    static const std::string uptime();
    static const std::string mem_max();
    static const std::string mem_available();

private:
    static const std::string cpu_freq_path;
    static const std::string cpu_temp_path;
    static const std::string uptime_path;
    // MemTotal:        3922640 kB      MemAvailable:    1153844 kB
    static const std::string mem_path;
    static std::string find_text(const std::string &txt, const std::string &substr);
    static char *read_the_command_line_output(const char *cmd);
};

/***************************************************************************************************/

const std::string Helper::cpu_freq_path = "/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq";
const std::string Helper::cpu_temp_path = "/sys/class/thermal/thermal_zone0/temp";
const std::string Helper::uptime_path   = "/proc/uptime";
const std::string Helper::mem_path      = "/proc/meminfo";

char *Helper::read_the_command_line_output(const char *cmd)
{
    FILE *fp_from_cmd = NULL;
	const char *type = "r";

    fp_from_cmd = popen(cmd, type);

    char *read_buf = (char *)malloc(128);
    char *output_string = (char *)malloc(4096 * 2); 
    memset(output_string, '\0', sizeof(output_string));

    while (!feof(fp_from_cmd))
    {
        memset(read_buf, '\0', sizeof(read_buf));
        // now start read cmd.
        fread(read_buf, 1, 1, fp_from_cmd);
        // fwrite(read_buf, 1, 1, stdout);
        strcat(output_string, read_buf);
    }
	// strcat(output_string, '\0');
    fclose(fp_from_cmd);
    free(read_buf);
    // free(output_string);
    return output_string;
}

std::string Helper::find_text(const std::string &txt, const std::string &substr)
{
    // 找到 'Model name:' 位置。
    auto pos_start = txt.find(substr);
    // 'Model name:' 以后的字符串。
    auto line_txt = txt.substr(pos_start);
    // 查找 'Model name:' 的换行符。
    auto pos_end = line_txt.find('\n');
    
    // 'Model name:          Cortex-A55'
    auto model = txt.substr(pos_start, pos_end);
    // 去除 'Model name:          '。
    auto model_name = model.substr(std::string(substr).length(), model.find('\n'));
    model_name.erase(std::remove(model_name.begin(), model_name.end(), ' '), model_name.end());
    return model_name;
}

const std::string Helper::cpu_model()
{
    const std::string lscpu_txt = Helper::read_the_command_line_output("lscpu");
    
    return Helper::find_text(lscpu_txt, "Model name:");
}

const std::string Helper::cpu_freq()
{
    std::string cmd = "cat ";
    cmd.append(Helper::cpu_freq_path);
    std::string txt = Helper::read_the_command_line_output(cmd.c_str());
    return txt.substr(0, std::string(txt).length() - 1);    // 去除行末换行
}

const std::string Helper::cpu_temp()
{
    std::string cmd = "cat ";
    cmd.append(Helper::cpu_temp_path);
    
    std::string txt = Helper::read_the_command_line_output(cmd.c_str());
    return txt.substr(0, std::string(txt).length() - 1);    // 去除行末换行
}

const std::string Helper::uptime()
{
    std::string cmd = "cat ";
    cmd.append(Helper::uptime_path);
    
    std::string txt = Helper::read_the_command_line_output(cmd.c_str());
    return txt.substr(0, std::string(txt).length() - 1);    // 去除行末换行
}

const std::string Helper::mem_max()
{
    std::string cmd = "cat ";
    cmd.append(Helper::mem_path);
    
    std::string txt = Helper::read_the_command_line_output(cmd.c_str());

    auto mem = Helper::find_text(txt, "MemTotal:");

    return mem.substr(0, std::string(mem).length() - 2);    // 去除行末换行和 'k'。
}

const std::string Helper::mem_available()
{
    std::string cmd = "cat ";
    cmd.append(Helper::mem_path);
    
    std::string txt = Helper::read_the_command_line_output(cmd.c_str());

    auto mem = Helper::find_text(txt, "MemAvailable:");

    return mem.substr(0, std::string(mem).length() - 2);    // 去除行末换行和 'k'。
}

#endif  // HELPER_HPP
