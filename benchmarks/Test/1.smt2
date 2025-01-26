(set-logic QF_UFNRA)
(set-option :produce-models true)

(declare-const x Real)

(assert (>= x 5))

; Minimize f
(minimize x)

(check-sat)
(get-objectives)
(get-model)
(exit)
