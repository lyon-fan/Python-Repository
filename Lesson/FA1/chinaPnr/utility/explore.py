# Index
# ----------------------------------------
# get_list_for_number_str_col 将dataframe中的字段名称分为字符型、数值型两个list返回
# num_var_perf    探索数值型变量的分布
# str_var_pref    探索字符型变量的分布

def get_list_for_number_str_col(p_df, p_col_id, p_col_target):
    """
    将dataframe中的字段名称分为数值型、字符型两个list返回
    :param p_df: 数据集
    :param p_col_id: 主键字段名
    :param p_col_target: 目标字段名
    :return:str_var_list: 字符型变量列表；numberVarlist- 数值型变量列表
    """
    import numpy as np

    name_of_col = list(p_df.columns)
    name_of_col.remove(p_col_target)
    name_of_col.remove(p_col_id)
    num_var_list = []
    str_var_list = []

    str_var_list = name_of_col.copy()
    for varName in name_of_col:
        if p_df[varName].dtypes in (np.int, np.int64, np.uint, np.int32, np.float, np.float64, np.float32, np.double):
            str_var_list.remove(varName)
            num_var_list.append(varName)
    print("function get_list_for_number_str_col finished!...................")
    return str_var_list, num_var_list


def num_var_perf(p_df, p_var_list, p_target_var, p_path, p_truncation=False):
    """
    探索数值型变量的分布
    :param p_df: 数据集
    :param p_var_list:数值型变量名称列表 List类型
    :param p_target_var: 响应变量名称
    :param p_path: 保存图片的位置
    :param p_truncation: 是否对数据做95%盖帽处理 默认不盖帽
    :return:
    """
    import numpy as np
    from matplotlib import pyplot
    import chinaPnr.utility.others as u_others

    frame_name = "num"

    u_others.create_frame(p_path, frame_name)

    for var in p_var_list:
        # 利用NaN != NaN的特性 将所有空值排除
        valid_df = p_df.loc[p_df[var] == p_df[var]][[var, p_target_var]]
        rec_perc = 100.0*valid_df.shape[0] / p_df.shape[0]
        rec_perc_fmt = "%.2f%%" % rec_perc
        desc = valid_df[var].describe()
        value_per50 = '%.2e' % desc['50%']
        value_std = '%.2e' % desc['std']
        value_mean = '%.2e' % desc['mean']
        value_max = '%.2e' % desc['max']
        value_min = '%.2e' % desc['min']
        # 样本权重
        bad_df = valid_df.loc[valid_df[p_target_var] == 1][var]
        good_df = valid_df.loc[valid_df[p_target_var] == 0][var]
        bad_weight = 100.0*np.ones_like(bad_df)/bad_df.size
        good_weight = 100.0*np.ones_like(good_df)/good_df.size
        # 是否用95分位数进行盖帽
        if p_truncation:
            per95 = np.percentile(valid_df[var], 95)
            bad_df = bad_df.map(lambda x: min(x, per95))
            good_df = good_df.map(lambda x: min(x, per95))
        # 画图
        fig, ax = pyplot.subplots()
        ax.hist(bad_df, weights=bad_weight, alpha=0.3, label='bad')
        ax.hist(good_df, weights=good_weight, alpha=0.3, label='good')
        title_text = var + '\n' \
                     + 'VlidePerc:' \
                     + rec_perc_fmt \
                     + ';Mean:' \
                     + value_mean \
                     + ';Per50:' + value_per50 \
                     + ';Std:' + value_std \
                     + ';\n' \
                     + 'Max:' + value_max \
                     + ';Min:'+value_min
        ax.set(title=title_text, ylabel='% of dataset in bin')
        ax.margins(0.05)
        ax.set_ylim(bottom=0)
        pyplot.legend(loc='upper right')
        fig_save_path = p_path + '\\' + str(var) + '.png'
        pyplot.savefig(fig_save_path)
        pyplot.close(1)
        u_others.add_index_html(p_path, frame_name, var)
        # pyplot.show()
    print("function num_var_perf finished!...................")


def str_var_pref(p_df, p_var_list, p_target_var, p_path):
    """
    探索字符型变量的分布
    :param p_df: 数据集
    :param p_var_list: 字符型型变量名称列表 List类型
    :param p_target_var: 响应变量名称
    :param p_path: 保存图片的位置
    :return:
    """
    import pandas as pd
    from matplotlib import pyplot
    import chinaPnr.utility.others as u_others

    frame_name = "str"
    u_others.create_frame(p_path, frame_name)

    for var in p_var_list:
        # 利用None != None的特性 将所有空值排除
        valid_df = p_df.loc[p_df[var] == p_df[var]][[var, p_target_var]]
        rec_perc = 100.0*valid_df.shape[0] / p_df.shape[0]
        rec_perc_fmt = "%.2f%%" % rec_perc
        dict_freq = {}
        dict_bad_rate = {}
        for v in set(valid_df[var]):
            v_df = valid_df.loc[valid_df[var] == v]
            # 每个类别数量占比
            dict_freq[v] = 1.0*v_df.shape[0] / p_df.shape[0]
            # 每个类别坏客户占比
            dict_bad_rate[v] = sum(v_df[p_target_var] * 1.0) / v_df[p_target_var].shape[0]

        if p_df.loc[p_df[var] != p_df[var]][p_target_var].shape[0] > 0:
            # 当前变量缺失率统计
            dict_freq['missValue'] = 1.0 - valid_df.shape[0] / p_df.shape[0]
            # 当前变量缺失率值中坏商户占比
            dict_bad_rate['missValue'] = \
                sum(p_df.loc[p_df[var] != p_df[var]][p_target_var]) \
                / p_df.loc[p_df[var] != p_df[var]][p_target_var].shape[0]
        desc_state = pd.DataFrame({'percent': dict_freq, 'bad rate': dict_bad_rate})
        # 画图
        fig = pyplot.figure()
        ax0 = fig.add_subplot(111)
        ax1 = ax0.twinx()
        pyplot.title('The percentage and bad rate for '+var+'\n valid rec_perc ='+rec_perc_fmt)
        desc_state.percent.plot(kind='bar', color='blue', ax=ax0, width=0.2, position=1)
        desc_state['bad rate'].plot(kind='line', color='red', ax=ax1)
        ax0.set_ylabel('percent(bar)')
        ax1.set_ylabel('bad rate(line)')
        fig_save_path = p_path + '\\' + str(var) + '.png'
        pyplot.savefig(fig_save_path)
        pyplot.close(1)
        u_others.add_index_html(p_path, frame_name, var)
    print("function str_var_pref finished!...................")