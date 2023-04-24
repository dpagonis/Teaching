import csv
from mendeleev import element

# Define the properties to include in the CSV
properties = [
    'abundance_crust', 'abundance_sea', 'annotation', 'atomic_number', 'atomic_radius', 'atomic_radius_rahm', 'atomic_volume', 'atomic_weight', 'atomic_weight_uncertainty', 'block', 'boiling_point', 'c6', 'c6_gb', 'cas', 'covalent_radius', 'covalent_radius_bragg', 'covalent_radius_cordero', 'covalent_radius_pyykko', 'covalent_radius_pyykko_double', 'covalent_radius_pyykko_triple', 'cpk_color', 'density', 'description', 'dipole_polarizability', 'dipole_polarizability_unc', 'discoverers', 'discovery_location', 'discovery_year', 'ec', 'econf', 'electron_affinity', 'electronegativity', 'electronegativity_allen', 'electronegativity_allred_rochow', 'electronegativity_cottrell_sutton', 'electronegativity_ghosh', 'electronegativity_gordy', 'electronegativity_li_xue', 'electronegativity_martynov_batsanov', 'electronegativity_mulliken', 'electronegativity_nagle', 'electronegativity_pauling', 'electronegativity_sanderson', 'electronegativity_scales', 'electrons', 'electrophilicity', 'en_allen', 'en_ghosh', 'en_pauling', 'evaporation_heat', 'fusion_heat', 'gas_basicity', 'geochemical_class', 'glawe_number', 'goldschmidt_class', 'group', 'group_id', 'hardness', 'heat_of_formation', 'inchi', 'init_on_load', 'ionenergies', 'ionic_radii', 'is_monoisotopic', 'is_radioactive', 'isotopes', 'jmol_color', 'lattice_constant', 'lattice_structure', 'mass', 'mass_number', 'mass_str', 'melting_point', 'mendeleev_number', 'metadata', 'metallic_radius', 'metallic_radius_c12', 'molar_heat_capacity', 'molcas_gv_color', 'name', 'name_origin', 'neutrons', 'nist_webbook_url', 'nvalence', 'oxidation_states', 'oxides', 'oxistates', 'period', 'pettifor_number', 'phase_transitions', 'proton_affinity', 'protons', 'registry', 'sconst', 'screening_constants', 'series', 'softness', 'sources', 'specific_heat', 'specific_heat_capacity', 'symbol', 'thermal_conductivity', 'uses', 'vdw_radius', 'vdw_radius_alvarez', 'vdw_radius_batsanov', 'vdw_radius_bondi', 'vdw_radius_dreiding', 'vdw_radius_mm3', 'vdw_radius_rt', 'vdw_radius_truhlar', 'vdw_radius_uff', 'zeff'
]

elements_data = []

for atomic_number in range(1, 119):
    elem = element(atomic_number)
    elem_data = {}
    for prop in properties:
        elem_data[prop] = getattr(elem, prop, None)
    elements_data.append(elem_data)

with open('elements.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = properties
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in elements_data:
        writer.writerow(data)

print("Elements data has been saved to elements.csv")