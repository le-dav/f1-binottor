import binottor.racesimulator.main_racesim_basic as basic
import binottor.racesimulator.racesim_basic.src.calc_racetimes_basic as lap_calc

import main_racesim_basic

def estimated_pace(laps,metrics,predicted=False):
    COMPOUND = {
        'SOFT': 'A5',
        'MEDIUM': 'A4',
        'HARD': 'A3'
    }

    if not laps.empty:
        strat = laps[laps['RealPitting']==True]
        list_of_laps = [i for i in strat.index]
        if list_of_laps[0] != 0:
            list_of_laps.insert(0,laps.index[0]-2)
        #if list_of_laps[-1] == :
        #list_of_laps.insert(-1,laps.index[-1])
    print(list_of_laps)
    if predicted == True :
        strat_predict = []
        compound_predict = []
        for index,i in enumerate(list_of_laps):
            if index < len(list_of_laps)-1:
                slice = laps.loc[i+2:list_of_laps[index+1]]
                print("Slice")
                print(slice)
                print(list_of_laps[index+1]+1)
                print(slice[slice.ModelPitting==1])
                index_predict = slice.index[0]
                print(index_predict)
                print(len(slice))
                if not len(slice[slice.ModelPitting==True])==0:
                    strat_predict.append(slice[slice.ModelPitting==True].iloc[0].LapNumber+1)
                    compound_predict.append(slice.iloc[-1].ModelCompound)
                else:
                    print(index)
                    strat_predict.append(laps.loc[list_of_laps[index+1]].LapNumber+1)
                    compound_predict.append(laps.loc[list_of_laps[index+1]].ModelCompound)
    strat_predict.insert(0,0)
    compound_predict.insert(0,0)
    # TO REMOVE
    #compound_predict.append('SOFT')
    #compound_predict.append('HARD')
    lap = laps.iloc[0]
    strategy = [[0, COMPOUND[lap['Compound']], lap['TyreLife'], 0.0]]
    strategy_predicted = [[0, COMPOUND[lap['Compound']], lap['TyreLife'], 0.0]]
    if not strat.empty:
        last_index = laps.index[-1]
        for index,row in strat.iterrows():
            if index+1<=last_index:
                strategy.append([int(laps.loc[index+2,"LapNumber"]),COMPOUND[laps.loc[index+2,'Compound']],0,0])
    if predicted==True:
        for i in range(1,len(strat_predict)):
            strategy_predicted.append([int(strat_predict[i]),COMPOUND[compound_predict[i]],0,0])

    print(f"Simulating {lap.Year} {lap.Location} GP real strat. from {lap.Driver} ({lap.Team})")
    print(f"Real strategy: {str(strategy)}")

    #sim_opts_ = {"min_no_pitstops": 0 if lap['second_compound']==True else 1,
    #             "max_no_pitstops": 3,
    #             "start_compound": COMPOUND[lap['Compound']],
    #             "start_age": lap['TyreLife'],
    #             "enforce_diff_compounds": not lap['second_compound'],
    #             "use_qp": False,
    #             "fcy_phases": None}

    driver_pars={"t_base": metrics[(metrics.Team==lap.Team) & (metrics.Location==lap.Location) & (metrics.Year==lap.Year)]['avg_laptime'].values[0],
             "p_grid": lap.Position,
             "tire_pars": {"tire_deg_model": "lin",
                           "t_add_coldtires": 1.0,
                           "A3": {"k_0": 1.2, "k_1_lin": 0.02, "k_1_ln": 0.2, "k_2_ln": 0.3},
                           "A4": {"k_0": 0.5, "k_1_lin": 0.05, "k_1_ln": 0.6, "k_2_ln": 0.3},
                           "A5": {"k_0": 0.0, "k_1_lin": 0.09, "k_1_ln": 1.0, "k_2_ln": 0.3}},
             "drivetype": "combustion",
             "t_pit_tirechange": 3.0, # Already included in t_pit_in et t_pit_out
             "m_fuel_init": int(1-lap['RaceProgress'])*100,
             "b_fuel_perlap": None,
             "t_pit_refuel_perkg": None,
             "t_pit_charge_perkwh": None}

    track_pars={"t_pitdrive_inlap": metrics[(metrics.Team==lap.Team) & (metrics.Location==lap.Location) & (metrics.Year==lap.Year)]['pit_in_time'].values[0],
            "t_pitdrive_outlap": metrics[(metrics.Team==lap.Team) & (metrics.Location==lap.Location) & (metrics.Year==lap.Year)]['pit_out_time'].values[0],
            "t_pitdrive_inlap_fcy": 0.8,
            "t_pitdrive_outlap_fcy": 12.6,
            "t_pitdrive_inlap_sc": 0.0,
            "t_pitdrive_outlap_sc": 10.5,
            "pits_aft_finishline": True,
            "t_lap_fcy": None,
            "t_lap_sc": None,
            "t_lap_sens_mass": 0.03,
            "t_loss_pergridpos": 0,
            "t_loss_firstlap": 0}
    race_pars={"tot_no_laps": int(laps.LapNumber.max()-lap.LapNumber)}
    pars_in = {'race_pars': race_pars,
               'track_pars': track_pars,
               'driver_pars':driver_pars}

    pars_in['available_compounds'] = [key for key in pars_in['driver_pars']["tire_pars"].keys()
                                      if key in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'I', 'W']]

    if pars_in['driver_pars']["drivetype"] == "combustion" and pars_in['driver_pars']["b_fuel_perlap"] is None:
        # calculate approximate fuel consumption per lap
        pars_in['driver_pars']["b_fuel_perlap"] = (pars_in['driver_pars']["m_fuel_init"]
                                                   / pars_in['race_pars']["tot_no_laps"])

    print(pars_in)
    print(strategy_predicted)
    t_race = lap_calc.calc_racetimes_basic(t_base=pars_in['driver_pars']["t_base"],
                                         tot_no_laps=pars_in['race_pars']["tot_no_laps"],
                                         t_lap_sens_mass=pars_in['track_pars']["t_lap_sens_mass"],
                                         t_pitdrive_inlap=pars_in['track_pars']["t_pitdrive_inlap"],
                                         t_pitdrive_outlap=pars_in['track_pars']["t_pitdrive_outlap"],
                                         t_pitdrive_inlap_fcy=pars_in['track_pars']["t_pitdrive_inlap_fcy"],
                                         t_pitdrive_outlap_fcy=pars_in['track_pars']["t_pitdrive_outlap_fcy"],
                                         t_pitdrive_inlap_sc=pars_in['track_pars']["t_pitdrive_inlap_sc"],
                                         t_pitdrive_outlap_sc=pars_in['track_pars']["t_pitdrive_outlap_sc"],
                                         t_pit_tirechange=pars_in['driver_pars']["t_pit_tirechange"],
                                         pits_aft_finishline=pars_in['track_pars']["pits_aft_finishline"],
                                         tire_pars=pars_in['driver_pars']["tire_pars"],
                                         p_grid=pars_in['driver_pars']["p_grid"],
                                         t_loss_pergridpos=pars_in['track_pars']["t_loss_pergridpos"],
                                         t_loss_firstlap=pars_in['track_pars']["t_loss_firstlap"],
                                         strategy=strategy,
                                         drivetype=pars_in['driver_pars']["drivetype"],
                                         m_fuel_init=pars_in['driver_pars']["m_fuel_init"],
                                         b_fuel_perlap=pars_in['driver_pars']["b_fuel_perlap"],
                                         t_pit_refuel_perkg=pars_in['driver_pars']["t_pit_refuel_perkg"],
                                         t_pit_charge_perkwh=pars_in['driver_pars']["t_pit_charge_perkwh"],
                                         fcy_phases=None,
                                         t_lap_sc=pars_in['track_pars']["t_lap_sc"],
                                         t_lap_fcy=pars_in['track_pars']["t_lap_fcy"])[0][-1]

    print(f"Predicted strategy: {str(strategy_predicted)}")

    t_predicted = lap_calc.calc_racetimes_basic(t_base=pars_in['driver_pars']["t_base"],
                                         tot_no_laps=pars_in['race_pars']["tot_no_laps"],
                                         t_lap_sens_mass=pars_in['track_pars']["t_lap_sens_mass"],
                                         t_pitdrive_inlap=pars_in['track_pars']["t_pitdrive_inlap"],
                                         t_pitdrive_outlap=pars_in['track_pars']["t_pitdrive_outlap"],
                                         t_pitdrive_inlap_fcy=pars_in['track_pars']["t_pitdrive_inlap_fcy"],
                                         t_pitdrive_outlap_fcy=pars_in['track_pars']["t_pitdrive_outlap_fcy"],
                                         t_pitdrive_inlap_sc=pars_in['track_pars']["t_pitdrive_inlap_sc"],
                                         t_pitdrive_outlap_sc=pars_in['track_pars']["t_pitdrive_outlap_sc"],
                                         t_pit_tirechange=pars_in['driver_pars']["t_pit_tirechange"],
                                         pits_aft_finishline=pars_in['track_pars']["pits_aft_finishline"],
                                         tire_pars=pars_in['driver_pars']["tire_pars"],
                                         p_grid=pars_in['driver_pars']["p_grid"],
                                         t_loss_pergridpos=pars_in['track_pars']["t_loss_pergridpos"],
                                         t_loss_firstlap=pars_in['track_pars']["t_loss_firstlap"],
                                         strategy=strategy_predicted,
                                         drivetype=pars_in['driver_pars']["drivetype"],
                                         m_fuel_init=pars_in['driver_pars']["m_fuel_init"],
                                         b_fuel_perlap=pars_in['driver_pars']["b_fuel_perlap"],
                                         t_pit_refuel_perkg=pars_in['driver_pars']["t_pit_refuel_perkg"],
                                         t_pit_charge_perkwh=pars_in['driver_pars']["t_pit_charge_perkwh"],
                                         fcy_phases=None,
                                         t_lap_sc=pars_in['track_pars']["t_lap_sc"],
                                         t_lap_fcy=pars_in['track_pars']["t_lap_fcy"])[0][-1]

    print(f"Estimated race time with real strategy: {t_race}")
    print(f"Estimated race time with predicted strategy: {t_predicted}")
    print("===========================")
    return t_race, t_predicted, strategy, strategy_predicted
