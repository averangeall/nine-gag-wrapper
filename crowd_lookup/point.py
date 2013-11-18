# Recomm:

#     how many points will a user query/hate affect a keyword?
RECOMM_VAL_POINT = 0.9

#     how many points required to be visible to everyone?
MIN_RECOMM_VISIBLE_POINT = 1.5


# Explain:

#     how many points will a user like/hate affect a explain?
EXPL_VAL_POINT = 0.9

#     how many points required to be visible to everyone?
MIN_EXPL_VISIBLE_POINT = 0.0

#     what is the initial point of a explain from a user?
PROVIDE_EXPL_INIT_POINT = 2.0

#     how many points will be decreased if one hate his/her own expl?
SELF_HATE_EXPL_POINT = 20.0

#     what is the maximum initial point of a explain from google translate?
GT_EXPL_INIT_POINT = 1.4

#     what is the maximum initial point of a explain from urban dictionary?
UD_NO_GT_EXPL_INIT_POINT = 1.2
UD_WITH_GT_EXPL_INIT_POINT = 0.3

#     what is the maximum initial point of a explain from google image?
GI_WITH_QM_EXPL_INIT_POINT = 0.6
GI_NO_QM_EXPL_INIT_POINT = 1.1

#     what is the maximum initial point of a explain from urban dictionary?
YT_EXPL_INIT_POINT = 0.7

#     what is the maximum initial point of a explain from quick meme?
QM_EXPL_INIT_POINT = 1.0

