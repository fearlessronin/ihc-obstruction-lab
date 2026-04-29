# Association Rules

Rules mined from seed dataset.

Parameters:
- max antecedent size 2
- min confidence 0.8
- seed records 12

| antecedent | consequent | support count | support | confidence | lift |
| --- | --- | ---: | ---: | ---: | ---: |
| has_local_package | status_calibration_row | 6 | 0.50 | 1.00 | 1.33 |
| has_local_package, trust_gold_hand_verified | status_calibration_row | 6 | 0.50 | 1.00 | 1.33 |
| trust_gold_hand_verified | status_calibration_row | 6 | 0.50 | 1.00 | 1.33 |
| computability_level_2_computed_group | status_calibration_row | 5 | 0.42 | 1.00 | 1.33 |
| computability_level_2_computed_group, has_local_package | status_calibration_row | 5 | 0.42 | 1.00 | 1.33 |
| computability_level_2_computed_group, trust_gold_hand_verified | status_calibration_row | 5 | 0.42 | 1.00 | 1.33 |
| computability_level_2_computed_group, local_group_nontrivial | channel_local_discriminant | 4 | 0.33 | 1.00 | 2.40 |
| has_local_package, local_group_nontrivial | channel_local_discriminant | 4 | 0.33 | 1.00 | 2.40 |
| local_group_nontrivial | channel_local_discriminant | 4 | 0.33 | 1.00 | 2.40 |
| local_group_nontrivial, trust_gold_hand_verified | channel_local_discriminant | 4 | 0.33 | 1.00 | 2.40 |
| computability_level_2_computed_group, local_group_nontrivial | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| computability_level_2_computed_group, op_smith_normal_form | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| has_local_package, local_group_nontrivial | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| has_local_package, op_smith_normal_form | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| local_group_nontrivial | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| local_group_nontrivial, trust_gold_hand_verified | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| op_smith_normal_form | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| op_smith_normal_form, trust_gold_hand_verified | status_calibration_row | 4 | 0.33 | 1.00 | 1.33 |
| computability_level_3_theorem_import, op_global_relation | bottleneck_global_relation_rank | 3 | 0.25 | 1.00 | 4.00 |
| computability_level_3_theorem_import, op_global_relation | channel_nodal_free_relation | 3 | 0.25 | 1.00 | 4.00 |
