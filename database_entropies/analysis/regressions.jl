using SQLite
using DataFrames
using CSV
using Optim
using Random

# Load the data
function fetch_data(db_file_path::String)
    db = SQLite.DB(db_file_path)
    query = "SELECT trans_S, rot_S, vib_S, epsilon, experimental_S FROM molecules"
    data = DBInterface.execute(db, query) |> DataFrame
    SQLite.close(db)
    return data
end

function prepare_data(data::DataFrame)
    return dropmissing(data)
end

# Objective functions
function obj_model(coeffs, srot, strans, svib, s_exp, model)
    if model == 1
        predictions = coeffs[1]*(srot .+ strans) .+ coeffs[2]*svib
    elseif model == 2
        predictions = coeffs[1]*strans .+ coeffs[2]*srot .+ coeffs[3]*svib
    elseif model == 3
        predictions = coeffs[1]*(strans .+ srot) .+ coeffs[2]*svib .+ coeffs[3] * (strans.*svib .+ srot.*svib)
    elseif model == 4
        predictions = coeffs[1]*strans .+ coeffs[2]*srot .+ coeffs[3]*svib .+ coeffs[4]*(strans.*svib) .+ coeffs[5] * (srot.*svib)
    else
        error("Unknown model")
    end
    return sum((s_exp .- predictions) .^ 2)
end

function optimize_model(srot, strans, svib, s_exp, model, bounds, num_coeffs)
    lower_bounds = [b[1] for b in bounds]
    upper_bounds = [b[2] for b in bounds]
    initial_guess = rand(num_coeffs)
    result = optimize(coeffs -> obj_model(coeffs, srot, strans, svib, s_exp, model),
                      initial_guess,
                      lower_bounds,
                      upper_bounds,
                      Fminbox())
    return result
end

function evaluate_models(data)
    srot, strans, svib, s_exp = data.rot_S, data.trans_S, data.vib_S, data.experimental_S
    # models
    models = [
        (1, [(0, 1), (0, 1)], 2, "α*(S_r + S_t) + β*S_v"),
        (2, [(0, 1), (0, 1), (0, 1)], 3, "α*S_t + β*S_r + γ*S_v"),
        (3, [(0, 1), (0, 1), (0, 1)], 3, "α*(S_t + S_r) + β*S_v + γ*(S_tv)"),
        (4, [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], 5, "α*S_t + β*S_r + γ*S_v + δ*(S_tv) + ε*(S_rv)")
    ]
    #
    for (model, bounds, num_coeffs, formula) in models
        result = optimize_model(srot, strans, svib, s_exp, model, bounds, num_coeffs)
        if result.converged
            coeffs = Optim.minimizer(result)
            predictions = coeffs[1] * (srot .+ strans) .+ coeffs[2] * svib  # Example for model 1
            if model == 2
                predictions = coeffs[1] * strans .+ coeffs[2] * srot .+ coeffs[3] * svib
            elseif model == 3
                predictions = coeffs[1] * (strans .+ srot) .+ coeffs[2] * svib .+ coeffs[3] * (strans .* svib .+ srot .* svib)
            elseif model == 4
                predictions = coeffs[1] * strans .+ coeffs[2] * srot .+ coeffs[3] * svib .+ coeffs[4] * (strans .* svib) .+ coeffs[5] * (srot .* svib)
            end
            mae = mean(abs.(s_exp .- predictions))
            println("Model: S = $formula")
            println("MAE for model $model: $mae")
        end
    end
end

function main()
    data = fetch_data("../entropiesCOSMO.db")
    data = prepare_data(data)
    evaluate_models(data)
end

main()

