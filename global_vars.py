from nbt import nbt

weapons = dict()
items = dict()
dmg_multipliers = dict()
enemies = dict()
generation_noise = dict()


def load_dmg_multipliers(tag: nbt.TAG_Compound):
    for dmg_applicant in tag.tags:
        target = dict()
        for dmg_recipient in dmg_applicant.tags:
            target[dmg_recipient.name] = dmg_recipient.value
        dmg_multipliers[dmg_applicant.name] = target


def load_generation_noise(tag: nbt.TAG_Compound):
    for origin in tag.tags:
        target = dict()
        for noise in origin.tags:
            target[noise.name] = noise.value
        generation_noise[origin.name] = target
    print(generation_noise)


def load_all(file: str = 'assets/files/data.nbt'):
    nbt_file = nbt.NBTFile(file, 'rb')
    load_dmg_multipliers(nbt_file['dmgMultipliers'])
    load_generation_noise(nbt_file['generationNoises'])


if __name__ == '__main__':
    load_all()
