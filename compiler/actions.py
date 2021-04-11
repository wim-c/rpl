
class Actions(object):
    def __init__(self, optimizer):
        super().__init__()
        self.optimizer = optimizer

    def unop_int(self):
        pass

    def unop_not(self):
        pass

    def binop_mul(self):
        pass

    def binop_add(self):
        pass

    def binop_sub(self):
        pass

    def binop_div(self):
        pass

    def binop_lt(self):
        pass

    def binop_le(self):
        pass

    def binop_ne(self):
        pass

    def binop_eq(self):
        pass

    def binop_gt(self):
        pass

    def binop_ge(self):
        pass

    def binop_mod(self):
        pass

    def binop_and(self):
        pass

    def binop_or(self):
        pass

    def and_word_const(self):
        pass

    def and_const_word(self):
        pass

    def or_word_const(self):
        pass

    def or_const_word(self):
        pass

    def push_if(self):
        pass

    def push_if_word(self):
        pass

    def push_label(self):
        pass

    def push_macro(self):
        pass

    def push_symbol(self):
        pass

    def unop_expr(self):
        pass

    def binop_expr_expr(self):
        pass

    def binop_expr_const(self):
        pass

    def unop_const(self):
        pass

    def binop_const_expr(self):
        pass

    def binop_const_const(self):
        pass

    def dup_word(self):
        pass

    def dup_ref(self):
        pass

    def dup_expr(self):
        pass

    def rot_word(self):
        pass

    def swap_const(self):
        pass

    def drop_const(self):
        pass

    def over_word(self):
        pass

    def over_ref(self):
        pass

    def over_expr(self):
        pass

    def pick_word(self):
        pass

    def mul_word(self):
        pass

    def add_word(self):
        pass

    def sub_word(self):
        pass

    def div_word(self):
        pass

    def and_word(self):
        pass

    def or_word(self):
        pass

    def lt_not(self):
        pass

    def le_not(self):
        pass

    def eq_not(self):
        pass

    def neq_not(self):
        pass

    def ge_not(self):
        pass

    def gt_not(self):
        pass

    def lt_swap(self):
        pass

    def le_swap(self):
        pass

    def ge_swap(self):
        pass

    def gt_swap(self):
        pass

    def symmetric_swap(self):
        pass

    def cancel_two(self):
        pass

    def implied(self):
        pass

    def mark_jmp(self):
        pass

    def mark_mark(self):
        pass

    def call_return(self):
        pass

    def jmp_skip(self):
        pass

    def beq_goto(self):
        pass
