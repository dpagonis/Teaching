from dp_qti import periodictable

pt = periodictable.periodictable()
pt.create_table(include_atomic_mass=False, sOut = 'pt/1200_pt_nomass') 
pt.create_table(sOut='pt/1200_pt')
pt.create_table(include_atomic_mass=False,additional_properties=['en_pauling'], sOut = 'pt/1200_pt_electronegativity') 
